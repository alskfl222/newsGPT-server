import re
from datetime import datetime
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


def get_analyzed_list(query):
    docs_analyzed = col_analyzed.find(
        query,
        {"_id": 0}
    )
    return list(docs_analyzed)
