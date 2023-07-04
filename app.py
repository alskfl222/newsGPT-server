import traceback
from fastapi import FastAPI
from pydantic import BaseModel
from search import get_search_list
from analyze import analyze_from_item
from db import export_db


class SearchModel(BaseModel):
    query: str
    source: str | None = None


app = FastAPI()


@app.get("/")
def health_check():
    return {"message": "OK"}


# @app.post("/search")
# def search_news_list(item: SearchItem):
#     query = item.query
#     search_list = get_search_list(query)
#     return search_list


@app.post("/analyze")
def analyze_news_for_query(body: SearchModel):
    query = body.query
    search_list = get_search_list(query)
    print('get search list')
    for news_item in search_list:
        title, url = news_item
        try:
            analyzed = analyze_from_item(query, title, url)
            if analyzed:
                export_db(analyzed)
            break
        except:
            traceback.print_exc()
            continue
    print(analyzed)
    return "OK?"
