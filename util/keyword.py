import datetime
import pymongo
from typing import List
from db import col_keywords


def set_keywords(keywords: List[str]):
    if not keywords:
        return "no keywords"
    doc_time = datetime.datetime.now()
    col_keywords.insert_one({"time": doc_time, "keywords": keywords})


def get_keywords_list(date_range: List[str]):
    try:
        start_string, end_string = date_range
        start = datetime.datetime.strptime(
            start_string, "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0)
        end = datetime.datetime.strptime(
            end_string, "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0)
    except:
        return "invaild date"
    docs_keywords = col_keywords.find(
        {"time": {"$gte": start, "$lte": end}},
        {"_id": 0, "time": 1, "keywords": 1},
        sort=[("time", pymongo.DESCENDING)]
    )

    return list(docs_keywords)


def get_keywords_in_date(date: str | None):
    if not date:
        date = datetime.datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)
    else:
        try:
            date = datetime.datetime.strptime(
                date, "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0)
        except:
            return "invaild date"
    next_date = date + datetime.timedelta(days=1)
    docs_keywords = col_keywords.find(
        {"time": {"$gte": date, "$lt": next_date}},
        {"_id": 0, "time": 1, "keywords": 1},
        sort=[("time", pymongo.DESCENDING)]
    ).limit(1)

    for doc in docs_keywords:
        keywords = doc['keywords']
        return keywords


def get_keywords_latest():
    docs = col_keywords.find(
        {},
        {"_id": 0, "time": 1, "keywords": 1},
        sort=[("time", pymongo.DESCENDING)]
    ).limit(1)
    for doc in docs:
        keywords = doc['keywords']
        return keywords


# def add_keywords(keywords: List[str]):
#     if not keywords:
#         return "no keywords"
#     docs = col_keywords.find(
#         {},
#         {"_id": 0, "time": 1, "keywords": 1},
#         # sort=[("time", pymongo.DESCENDING)]
#     ).limit(1)

#     keywords_last = docs.next()['keywords']

#     keywords_new = list(dict.fromkeys([*keywords_last, *keywords])) \
#         if keywords_last else keywords
#     doc_time = datetime.datetime.now()
#     col_keywords.insert_one({"time": doc_time, "keywords": keywords_new})
