from datetime import date
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel

from news.retrieve import *


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

@app.get("/latest")
def get_latest_news():
    latest_news = get_latest_news_by_keyword()
    return latest_news


@app.get("/news")
def get_news_list(
        page: Optional[int] = 1,
        start: Optional[date] = None,
        end: Optional[date] = None,
        keyword: Optional[str] = None,
        related: Optional[str] = None
    ):
    query = get_query(start=start, end=end,
                      keyword=keyword, related=related)
    analyzed_list = get_analyzed_list(page, query)
    return analyzed_list
