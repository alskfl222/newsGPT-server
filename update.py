import time
import tqdm
from util.search import get_search_list
from util.news.analyze import analyze_from_item
from util.news.retrieve import get_url_list
from util.keyword import get_keywords_latest
from util.log import log_db


def update_analyzed_news():
    keywords = get_keywords_latest()
    if not keywords:
        log_db("update_analyzed_news", "FAIL", error="no keywords")
        return
    url_list = get_url_list()
    for keyword in tqdm.tqdm(keywords):
        search_list = get_search_list(keyword)
        export_count = 0
        for item in search_list:
            url = item[1]
            if url in url_list or "msn.com" in url:
                continue
            result = analyze_from_item(keyword, item)
            if result:
                export_count += 1
            if export_count == 5:
                print(f"KEYWORD {keyword}: finished")
                break
        time.sleep(1)


if __name__ == "__main__":
    update_analyzed_news()
