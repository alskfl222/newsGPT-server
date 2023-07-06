import time
from news.search import get_search_list
from news.analyze import analyze_from_item
from news.retrieve import get_url_list
from news.keyword import get_keywords_latest
from util.log import log_db, log_result, printhl


def update_analyzed_news():
    keywords = get_keywords_latest()
    if not keywords:
        log_db("update_analyzed_news", "FAIL", error="no keywords")
        return
    url_list = get_url_list()
    count_dict = {}
    print()
    printhl(f"KEYWORDS: {keywords}")
    for keyword in keywords:
        search_list = get_search_list(keyword)
        print(f"KEYWORD: {keyword}")
        printhl(f"NEWS LIST LENGTH: {len(search_list)}", line="-")
        count_dict[keyword] = 0
        for item in search_list:
            title, url, provider = item
            print(f"NEWS TITLE: {title}")
            print(f"NEWS PROVIDER: {provider}")
            if url in url_list:
                printhl("EXIST", line='-')
                continue
            if "msn.com" in url:
                printhl("MSN.COM", line="-")
                continue
            result = analyze_from_item(keyword, item)
            if result:
                count_dict[keyword] += 1
                printhl("OK", line="-")
            else:
                printhl("ERROR", line="-")
            if count_dict[keyword] == 1:
                break
        printhl(f"KEYWORD {keyword}: FINISHED")
        time.sleep(1)
    print(f"NEWS ANALYZE COUNT: {count_dict}")
    log_result(count_dict)
    printhl("LOG COMPLETE")


if __name__ == "__main__":
    update_analyzed_news()
