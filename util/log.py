import datetime
from ..db import col_log

def log_db(fn_name: str, status: str, **kwargs):
    log = {
        "function": fn_name,
        "status": status,
        "time": datetime.datetime.now(),
        **kwargs,
    }
    col_log.insert_one(log)