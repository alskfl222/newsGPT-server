import time
from util.search import get_search_list
from util.news.analyze import analyze_from_item
from util.news.retrieve import get_url_list
from util.keyword import get_keywords_latest
from util.log import log_db, log_result


def update_analyzed_news():
    keywords = get_keywords_latest()
    if not keywords:
        log_db("update_analyzed_news", "FAIL", error="no keywords")
        return
    print(f"KEYWORDS: {keywords}")
    url_list = get_url_list()
    count_dict = {}
    print(f"{'='*50}")
    for keyword in keywords:
        print(f"KEYWORD: {keyword}")
        search_list = get_search_list(keyword)
        print(f"NEWS LIST LENGTH: {len(search_list)}")
        count_dict[keyword] = 0
        for item in search_list:
            title, url, provider = item
            print(f"NEWS TITLE: {title}")
            print(f"NEWS PROVIDER: {provider}")
            if url in url_list:
                print("EXIST")
                print(f"{'-'*50}")
                continue
            if "msn.com" in url:
                print("MSN.COM")
                print(f"{'-'*50}")
                continue
            result = analyze_from_item(keyword, item)
            if result:
                count_dict[keyword] += 1
                print("OK")
                print(f"{'-'*50}")
            else:
                print("ERROR")
                print(f"{'-'*50}")
            if count_dict[keyword] == 5:
                break
        print(f"KEYWORD {keyword}: FINISHED")
        print(f"{'='*50}")
        time.sleep(1)
    print(f"NEWS ANALYZE COUNT: {count_dict}")
    log_result(count_dict)
    print("LOG COMPLETE")
    print(f"{'='*50}")


if __name__ == "__main__":
    update_analyzed_news()
