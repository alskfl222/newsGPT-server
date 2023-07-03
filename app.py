from fastapi import FastAPI
from pydantic import BaseModel
from search import get_search_list
from analyze import analyze_from_url

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

    return search_list

@app.get("/analyze")
def news_analyze(url: str = ""):
    if not url:
        return "No url"
    analyzed = analyze_from_url(url)
    return analyzed