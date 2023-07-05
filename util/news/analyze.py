import traceback
import os
import datetime
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup, NavigableString
import openai
from ...db import col_analyzed
from ..log import log_db

openai.organization = "org-cfBhVIGyhj7tr2Fl15iay7Ln"
openai.api_key = os.getenv("OPENAI_API_KEY")


def extract_visible_text(soup: BeautifulSoup):
    if soup is None:
        return ""
    if isinstance(soup, NavigableString):
        return soup.strip() if soup.strip() else ""
    elif soup.name in ['style', 'script', 'head', 'title', 'meta']:
        return ""

    return " ".join(extract_visible_text(child) for child in soup.children)
    # return itertools.chain(*[extract_visible_text(child) for child in soup.children])


def remove_multiple_spaces(raw_text: str):
    return " ".join(raw_text.split())


def slice_text(raw_text: str, news_start: int, news_length: int):
    spaces_removed = " ".join(raw_text.split())
    sliced = spaces_removed[news_start:news_start+news_length]
    return sliced


def determine_sentiment(sentiment_string: str):
    if '긍정' in sentiment_string:
        return 'P'
    if '부정' in sentiment_string:
        return 'N'
    return 'E'


def request_analyze(search_keyword: str, sliced_text: str):
    analyze_string = f"""

        위 뉴스를 분석하고 결과를 다음 형식에 맞게 보여줘.
        검색어: {search_keyword}
        주제:
        긍정/부정: 검색어에 대해 긍정적인지 부정적인지
        키워드: 5개 까지만
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[{"role": "user", "content": sliced_text + analyze_string}],
        )

        raw: str = response['choices'][0]['message']['content']
        splited = raw.split("\n")
        analyzed = {"keyword": search_keyword, "time": datetime.datetime.now()}

        for string in splited:
            content = string.split(':')[-1].strip() \
                if string.split(':')[-1].strip() else ''
            if string.startswith('주제:'):
                analyzed['subject'] = content
            if string.startswith('긍정/부정:'):
                analyzed['P/N'] = determine_sentiment(content)
            if string.startswith('키워드:'):
                analyzed['related'] = [x.strip() for x in content.split(',')]

        return analyzed
    except:
        return {"keyword": search_keyword, "time": datetime.datetime.now(), "related": []}


def analyze_from_item(keyword, item):
    title, url, provider = item
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            page.goto(url, timeout=10000)

            soup = BeautifulSoup(page.content(), 'lxml')

            browser.close()

            extracted = extract_visible_text(soup)
            spaces_removed = remove_multiple_spaces(extracted)

            news_start = spaces_removed.find(title)
            news_length = 5000

            sliced_text = slice_text(spaces_removed, news_start, news_length)
            analyzed = {
                'title': title,
                'url': url,
                'provider': provider,
                **request_analyze(keyword, sliced_text)
            }

            # ! 분석 결과 판별 조건
            if len(analyzed['related']) > 2:
                log_db("analyze_from_item", "SUCCESS")
                col_analyzed.insert_one(analyzed)
                return True
            else:
                log_db("analyze_from_item", "FAIL",
                       message="GPT analyze fail", analyzed=analyzed)
                return False
    except:
        error_message = traceback.format_exc()
        log_db("analyze_from_item", "ERROR", error=error_message)
        return False
