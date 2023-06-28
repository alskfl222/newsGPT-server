import itertools
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup, NavigableString


def extract_visible_text(soup: BeautifulSoup):
    if soup is None:
        return ""
    if isinstance(soup, NavigableString):
        return soup.strip() if soup.strip() else ""
    elif soup.name in ['style', 'script', 'head', 'title', 'meta']:
        return ""

    return " ".join(extract_visible_text(child) for child in soup.children)
    # return itertools.chain(*[extract_visible_text(child) for child in soup.children])


def get_visible_texts_from_url(url):
    print(url)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        page.goto(url)
        print("goto url page")

        soup = BeautifulSoup(page.content(), 'html.parser')
        print("get soup")

        browser.close()

        return extract_visible_text(soup)
