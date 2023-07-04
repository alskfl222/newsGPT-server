import os
import datetime
from typing import List
import pymongo
import certifi
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("MONGODB_USER")
DB_PASSWORD = os.getenv("MONGODB_PASSWORD")
atlas_link = f"mongodb+srv://{DB_USER}:{DB_PASSWORD}@cluster0.tncf71y.mongodb.net/?retryWrites=true&w=majority"
db_client = pymongo.MongoClient(atlas_link, tlsCAFile=certifi.where())
db = db_client.newsGPT
col_log = db.log
col_keywords = db.keywords
col_analyzed = db.analyzed


def log_db(fn_name: str, status: str, **kwargs):
    print(kwargs)
    log = {
        "function": fn_name,
        "status": status,
        "time": datetime.datetime.now(),
        **kwargs,
    }
    col_log.insert_one(log)


# def log_success(fn_name: str, **kwargs):
#     log_db(fn_name, "SUCCESS", **kwargs)


# def log_error(fn_name: str, **kwargs):
#     log_db(fn_name, "ERROR", **kwargs)


def set_keywords(keywords: List[str]):
    if not keywords:
        return "no keywords"
    doc_time = datetime.datetime.now()
    col_keywords.insert_one({"time": doc_time, "keywords": keywords})


def get_keywords(date: str | None):
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
    )

    for doc in docs_keywords:
        print(doc)


def add_keywords(keywords: List[str]):
    if not keywords:
        return "no keywords"
    docs = col_keywords.find(
        {},
        {"_id": 0, "time": 1, "keywords": 1},
        # sort=[("time", pymongo.DESCENDING)]
    ).limit(1)

    keywords_last = docs.next()['keywords']

    keywords_new = list(dict.fromkeys([*keywords_last, *keywords])) \
        if keywords_last else keywords
    doc_time = datetime.datetime.now()
    col_keywords.insert_one({"time": doc_time, "keywords": keywords_new})


def export_db(analyzed):
    col_analyzed.insert_one(analyzed)

# set_keywords(['삼중수소', '태양광'])
# get_keywords("2023-07-04")
# add_keywords(['태양광', '방사능'])
