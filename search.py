import os
import requests
from dotenv import load_dotenv

load_dotenv()

BING_SEARCH_API_KEY = os.getenv("BING_SEARCH_API_KEY")
BING_SEARCH_API_URL = "https://api.bing.microsoft.com/v7.0/news/search"


def get_search_list(query):
    headers = {"Ocp-Apim-Subscription-Key": BING_SEARCH_API_KEY}

    # if source:
    #     bing_query = f"{query} {source}"
    # else:
    #     bing_query = f"{query}"

    search_list = []

    params = {"q": query, "freshness": "day", "count": 100}

    response = requests.get(BING_SEARCH_API_URL,
                            headers=headers, params=params)

    # if response.status_code != 200:
    #     continue

    data = response.json()

    search_list = [(x["name"], x["url"]) for x in data['value']]

    return search_list
