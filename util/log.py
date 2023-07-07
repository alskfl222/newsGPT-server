import datetime
from db import col_log, col_count


def printhl(*values, line='='):
    print(*values)
    print(f"{line*50}")


def log_db(fn_name: str, status: str, **kwargs):
    log = {
        "function": fn_name,
        "status": status,
        "time": datetime.datetime.now(),
        **kwargs,
    }
    col_log.insert_one(log)


def log_count(count):
    doc = {**count, "time": datetime.datetime.now()}
    col_count.insert_one(doc)
    log_db("log_count", "SUCCESS")
