import datetime
from db import col_log, col_result


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


def log_result(result):
    doc = {**result, "time": datetime.datetime.now()}
    col_result.insert_one(doc)
    log_db("log_result", "SUCCESS")
