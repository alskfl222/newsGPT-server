from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from search import get_search_list


class NewsItem(BaseModel):
    query: str
    source: str | None = None

app = FastAPI()



@app.get("/")
def health_check():
    return {"message": "OK"}


@app.post("/analyze")
def search_and_analyze(item: NewsItem):
    query = item.query

    search_list = get_search_list(query)
    print(len(search_list))
    print(search_list[0])

    return search_list

@app.get("/analyze")
def news_analyze(q: str = ""):
    if not q:
        return "No q"
    return q