from bson.objectid import ObjectId
from fastapi import HTTPException
from db import col_analyzed
from news.retrieve import get_news_by_id

def update_vote(news_id: str, vote: int):
    if vote == 1:
        col_analyzed.update_one({"_id": ObjectId(news_id)}, {"$inc": {"vote.true": 1}})
    elif vote == -1:
        col_analyzed.update_one({"_id": ObjectId(news_id)}, {"$inc": {"vote.false": 1}})
    else:
        raise HTTPException(400, "Invalid vote value")

    # 변경된 뉴스 가져오기
    updated_news = get_news_by_id(news_id)
    return updated_news