import os
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup, NavigableString
import openai

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

        위 뉴스를 분석해줘.
        상태: 성공, 분석이 안되면 실패
        검색어: {search_keyword}
        주제:
        긍정/부정: 검색어에 대해 긍정적인지 부정적인지
        키워드: 5개 까지만
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[{"role": "user", "content": sliced_text + analyze_string}],
    )
    print(response)
    return {"status": True, "response": response}


def analyze_from_url(url):
    print(url)
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

        news_start = 1000
        news_length = 10000
        while True:
            sliced_text = slice_text(spaces_removed, news_start, news_length)
            analyzed = request_analyze('태양광', sliced_text)
            if analyzed['status']:
                print('get analyzed')
                break
            else:
                news_start = news_start - 100 if news_start > 300 else 0
                news_length += 200

        return analyzed
