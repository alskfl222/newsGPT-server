import os
import requests
import traceback
from typing import List, Tuple
from dotenv import load_dotenv
from .log import log_db

load_dotenv()

BING_SEARCH_API_KEY = os.getenv("BING_SEARCH_API_KEY")
BING_SEARCH_API_URL = "https://api.bing.microsoft.com/v7.0/news/search"


def get_search_list(keyword) -> List[Tuple[str]]:
    headers = {"Ocp-Apim-Subscription-Key": BING_SEARCH_API_KEY}

    # if source:
    #     bing_keyword = f"{keyword} {source}"
    # else:
    #     bing_keyword = f"{keyword}"

    search_list = []

    params = {"q": keyword, "freshness": "day", "count": 100}
    try:
        response = requests.get(BING_SEARCH_API_URL,
                                headers=headers, params=params)

        # if response.status_code != 200:
        #     continue

        data = response.json()
        search_list = [(x["name"], x["url"], x["provider"][0]["name"]) for x in data['value']]

        return search_list
    except:
        error_message = traceback.format_exc()
        log_db("get_search_list", "ERROR", error=error_message)
        return []
