from datetime import date
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from news.keyword import *
from news.retrieve import *


class KeywordsModel(BaseModel):
    keywords: List[str]

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/keywords")
def get_latest_keywords():
    return get_keywords()


@app.put("/keywords")
def set_keywords_latest(body: KeywordsModel):
    return body.keywords
    # set_keywords()

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


@app.get("/news/{news_id}")
def get_news(news_id: str):
    news = get_news_by_id(news_id)
    if not news:
        raise HTTPException(404, "News not found")
    return news