import re
from datetime import datetime, timedelta
import pymongo
from bson.son import SON
from db import col_analyzed


def get_url_list():
    docs_analyzed = col_analyzed.find(
        {},
        {"_id": 0, "url": 1}
    )
    url_list = [x['url'] for x in docs_analyzed]
    return url_list


def get_query(**kwargs):
    query = {}

    if kwargs['start']:
        start = datetime.combine(kwargs['start'], datetime.min.time())
        query["time"] = {"$gte": start}

    if kwargs['end']:
        end = datetime.combine(kwargs['end'], datetime.max.time())
        query["time"] = {**query.get("time", {}), "$lte": end}

    if kwargs['keyword']:
        query["keyword"] = {
            "$regex": re.escape(kwargs['keyword']),
        }

    if kwargs['related']:
        query["related"] = {"$in": [kwargs['related']]}

    return query


def get_analyzed_list(page, query):
    docs_analyzed = col_analyzed.find(
        query,
        {"_id": 0},
        sort=[("time", pymongo.DESCENDING)]
    ).skip(page - 1).limit(10)
    return list(docs_analyzed)


def get_latest_news_by_keyword():
    today = datetime.now()
    yesterday = today - timedelta(days=1)

    pipeline = [
        # "time" 필드의 값이 오늘 날짜 혹은 어제 날짜인 문서만 선택합니다.
        {"$match": {"time": {"$gte": yesterday}}},
        # 각 문서를 키워드 별로 분리
        {"$unwind": "$keyword"},
        # 키워드와 시간으로 정렬
        {"$sort": SON([("keyword", 1), ("time", -1)])},
        # 키워드 별로 그룹화하고 각 그룹의 처음 3개 문서를 수집
        {"$group": {"_id": "$keyword", "docs": {"$push": "$$ROOT"}}},
        # 각 document에서 "_id" 필드 제외
        {"$project": {"docs": {"_id": 0}}},
        {"$project": {"_id": 1, "docs": {"$slice": ["$docs", 3]}}}
    ]

    result = col_analyzed.aggregate(pipeline)

    # 결과를 딕셔너리 형태로 변환
    latest_docs_by_keyword = {item['_id']: item['docs'] for item in result}
    return latest_docs_by_keyword
