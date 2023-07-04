import traceback
import os
import datetime
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup, NavigableString
import openai
from db import log_db

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


def request_analyze(search_keyword: str, sliced_text: str):
    analyze_string = f"""

        위 뉴스를 분석하고 결과를 다음 형식에 맞게 보여줘.
        상태: 분석 되면 성공, 안되면 실패
        검색어: {search_keyword}
        주제:
        긍정/부정: 검색어에 대해 긍정적인지 부정적인지
        키워드: 5개 까지만
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[{"role": "user", "content": sliced_text + analyze_string}],
    )

    raw: str = response['choices'][0]['message']['content']
    splited = raw.split("\n")
    analyzed = {"keyword": search_keyword, "time": datetime.datetime.now()}

    for string in splited:
        content = string.split(
            ':')[-1].strip() if string.split(':')[-1] else ''
        if string.startswith("상태:"):
            analyzed['status'] = True if content == '성공' else False
        if string.startswith('주제:'):
            analyzed['subject'] = content
        if string.startswith('긍정/부정:'):
            analyzed['P/N'] = 'P' if content.startswith('긍정') else 'N'
        if string.startswith('키워드:'):
            analyzed['related'] = [x.strip() for x in content.split(',')]

    return analyzed


def analyze_from_item(query, title, url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        page.goto(url, timeout=10000)
        print("goto url page")

        soup = BeautifulSoup(page.content(), 'lxml')
        print("get soup")

        browser.close()

        extracted = extract_visible_text(soup)
        spaces_removed = remove_multiple_spaces(extracted)

        news_start = spaces_removed.find(title)
        news_length = 5000

        sliced_text = slice_text(spaces_removed, news_start, news_length)
        analyzed = request_analyze(query, sliced_text)
        print(analyzed)
        if analyzed['status']:
            print('get analyzed')
            analyzed['title'] = title
            log_db("analyze_from_item", "SUCCESS")
            del analyzed['status']
            return analyzed
        else:
            print('analyze fail')
            error_message = traceback.format_exc()
            log_db("analyze_from_item", "FAIL", error=error_message)
            return
