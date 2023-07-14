import re
from datetime import datetime, timedelta
import pymongo
from bson.son import SON
from bson.objectid import ObjectId
from db import col_keywords, col_analyzed


def get_keywords():
    docs_keywords = col_keywords.find(
        {},
        {"_id": 0},
        sort=[("time", pymongo.DESCENDING)]
    ).limit(1)
    return docs_keywords.next()

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
        sort=[("time", pymongo.DESCENDING)]
    ).skip(page - 1).limit(10)
    return [{**x, '_id': str(x['_id'])} for x in docs_analyzed]


def get_latest_news_by_keyword():
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
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
        # {"$project": {"docs": {"_id": 0}}},
        {"$project": {"_id": 1, "docs": {"$slice": ["$docs", 3]}}}
    ]

    response = col_analyzed.aggregate(pipeline)
    
    # 결과를 딕셔너리 형태로 변환, _id는 문자열로 변환
    latest_docs_by_keyword = {
        item['_id']: [{**doc, '_id': str(doc['_id'])} for doc in item['docs']]
        for item in response
    }
    doc_keywords = get_keywords()
    latest_keywords = doc_keywords['keywords']
    remain_keywords = set(latest_docs_by_keyword.keys()) - set(latest_keywords)
    remain_keywords_sorted = sorted(remain_keywords, key=lambda x: x.lower())

    # 키워드별 결과 정렬
    result = {}
    for keyword in latest_keywords + remain_keywords_sorted:
        result[keyword] = latest_docs_by_keyword[keyword]

    return result


def get_news_by_id(id: str):
    try:
        object_id = ObjectId(id)
    except:
        return None
    news = col_analyzed.find_one({'_id': object_id})
    if news:
        news['_id'] = str(news['_id'])
        return news
    else:
        return None
