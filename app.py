from datetime import date
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel

from util.news.retrieve import get_query, get_analyzed_list


class SearchModel(BaseModel):
    keyword: str
    source: str | None = None


app = FastAPI()


@app.get("/")
def health_check():
    return {"message": "OK"}


# @app.post("/search")
# def search_news_list(item: SearchItem):
#     keyword = item.keyword
#     search_list = get_search_list(keyword)
#     return search_list


@app.get("/news")
def get_news_list(start: Optional[date] = None, end: Optional[date] = None, keyword: Optional[str] = None, related: Optional[str] = None):
    query = get_query(start=start, end=end, keyword=keyword, related=related)
    print(query)
    analyzed_list = get_analyzed_list(query)
    return analyzed_list
