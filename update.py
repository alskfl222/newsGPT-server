import time
from news.search import get_search_list
from news.analyze import get_model_list, analyze_from_item
from news.retrieve import get_url_list
from news.keyword import get_keywords_latest
from util.log import log_db, log_count, printhl


def update_analyzed_news(model=''):
    if not model:
        log_db("update_analyzed_news", "FAIL", error="no suitable model")
        return
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
        count_dict[keyword] = {
            'searched': len(search_list), 
            'analyzed': 0, 
            'tokens': 0
        }
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
            result, tokens = analyze_from_item(model, keyword, item)
            count_dict[keyword]['tokens'] += tokens
            if result:
                count_dict[keyword]['analyzed'] += 1
                printhl("OK", line="-")
            else:
                printhl("ERROR", line="-")
            # break
            if count_dict[keyword]['analyzed'] == 10:
                break
        printhl(f"KEYWORD {keyword}: FINISHED")
        time.sleep(1)
    print(f"NEWS ANALYZE COUNT: {count_dict}")
    log_count(count_dict)
    printhl("LOG COMPLETE")


if __name__ == "__main__":
    print("UPDATE START")
    model_list = get_model_list()
    print("AVAILABLE MODEL LIST")
    printhl(model_list)
    model = ''
    if 'gpt-4-8k' in model_list:
        model = 'gpt-4-8k'
    elif 'gpt-3.5-turbo-16k' in model_list:
        model = 'gpt-3.5-turbo-16k'
    printhl(f"ANALYZE MODEL: {model}")
    update_analyzed_news(model=model)
