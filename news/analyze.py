import traceback
import os
import json
import datetime
import pytz
from dateutil.parser import parse
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup, NavigableString
import openai
from db import col_analyzed
from util.log import log_db

openai.organization = "org-cfBhVIGyhj7tr2Fl15iay7Ln"
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_model_list():
    response = openai.Model.list()
    return [x['id'] for x in response['data']]


def extract_visible_text(soup: BeautifulSoup):
    if soup is None:
        return ""
    if isinstance(soup, NavigableString):
        return soup.strip() if soup.strip() else ""
    elif soup.name in ['style', 'script', 'head', 'title', 'meta']:
        return ""

    return " ".join(extract_visible_text(child) for child in soup.children)


def remove_multiple_spaces(raw_text: str):
    return " ".join(raw_text.split())


def slice_text(raw_text: str, news_start: int, news_length: int):
    spaces_removed = " ".join(raw_text.split())
    sliced = spaces_removed[news_start:news_start+news_length]
    return sliced


def determine_sentiment(sentiment_string: str):
    if '긍정' in sentiment_string:
        return 'P'
    if '부정' in sentiment_string:
        return 'N'
    return 'E'


def process_analyzed(
    status: str,
    topic: str,
    overall_sentiment: str,
    keyword_sentiment: str,
    related: str,
    upload_time="0001-01-01"
):
    """To processing news analyzed result"""
    now = datetime.datetime.now(pytz.timezone('Asia/Seoul'))
    upload_datetime = parse(upload_time) if parse(
        upload_time) < now else parse("0001-01-01")
    processed = {
        "status": True if status == "Success" else False,
        "topic": topic,
        "upload_time": upload_datetime.isoformat(),
        "sentiment": {
            "overall": overall_sentiment,
            "keyword": keyword_sentiment,
        },
        "related": [x.strip() for x in related.split(',')]
    }
    return json.dumps(processed)


def request_analyze(model: str, search_keyword: str, sliced_text: str):
    request_analyze_string = f"""
    
        Please analyze the news and display the results in the following format:
        - Status: Success if analyzed, Failure otherwise
        - Search keyword: {search_keyword}
        - Topic: Translate into Korean
        - Upload time: In ISO format
        - Overall sentiment: The overall tone or sentiment carried by the news piece
        - Keyword sentiment: Whether it is Positive or Negative about the search keyword, If it is hard to judge, it can be Equal
        - Keywords: Up to 5 only, in Korean, separated by commas
    """
    functions = [
        {
            "name": "process_analyzed",
            "description": "To processing news analyzed result",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Analyzing status, Success if analyzed, Failure otherwise",
                        "enum": ["Success", "Failure"]
                    },
                    "topic": {
                        "type": "string",
                        "description": "topic of the analyzed news in Korean"
                    },
                    "upload_time": {
                        "type": "string",
                        "description": "Upload time of the news on the webpage, formatted in ISO"
                    },
                    "overall_sentiment": {
                        "type": "string",
                        "description": "The overall tone or sentiment carried by the news piece",
                        "enum": ["Positive", "Negative", "Equal"]
                    },
                    "keyword_sentiment": {
                        "type": "string",
                        "description": "Whether this news is positive, negative, or neutral towards the search keyword",
                        "enum": ["Positive", "Negative", "Equal"]
                    },
                    "related": {
                        "type": "string",
                        "description": "Associated keywords analyzed from the news, up to 5, separated by commas, in Korean"
                    }
                },
                "required": ["status", "topic", "upload_time", "overall_sentiment", "keyword_sentiment", "related"],
            },
        }
    ]
    available_functions = {
        "process_analyzed": process_analyzed
    }
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "user", "content": sliced_text + request_analyze_string}
            ],
            functions=functions,
            function_call="auto"
        )
        response_message = response['choices'][0]['message']

        if response_message.get("function_call"):
            function_name = response_message["function_call"]["name"]
            function_to_call = available_functions[function_name]
            function_args = json.loads(
                response_message["function_call"]["arguments"])
            function_response_raw = function_to_call(
                status=function_args.get("status"),
                topic=function_args.get("topic"),
                overall_sentiment=function_args.get("overall_sentiment"),
                keyword_sentiment=function_args.get("keyword_sentiment"),
                related=function_args.get("related"),
                upload_time=function_args.get("upload_time")
            )
            tokens: int = response['usage']['total_tokens']
            print(f"TOTAL TOKENS: {tokens}")

            result = {
                **json.loads(function_response_raw),
                "tokens": tokens,
            }
            return result
        else:
            print("FUNCTION CANNOT BE CALLED")
            return {}

    except:
        traceback.print_exc()
        error_result = {
            "related": []
        }
        try:
            return {**error_result, "tokens": tokens}
        except:
            return {**error_result, "tokens": 0}


def analyze_from_item(model: str, keyword: str, item: tuple[str]) -> tuple[bool, int]:
    title, url, provider = item
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            page.goto(url, timeout=10000)

            soup = BeautifulSoup(page.content(), 'lxml')

            browser.close()

            extracted = extract_visible_text(soup)
            spaces_removed = remove_multiple_spaces(extracted)

            news_start = spaces_removed.find(title)
            news_length = 4000

            sliced_text = slice_text(spaces_removed, news_start, news_length)
            analyzed = {
                'keyword': keyword,
                'title': title,
                'url': url,
                'provider': provider,
                'time': datetime.datetime.now(),
                'vote': {
                    'true': 0,
                    'false': 0,
                },
                **request_analyze(model, keyword, sliced_text)
            }

            # ! 분석 결과 판별 조건
            if 'status' in analyzed and analyzed['status']:
                # if 'status' in analyzed:
                log_db("analyze_from_item", "SUCCESS")
                del analyzed['status']
                col_analyzed.insert_one(analyzed)
                return True, analyzed['tokens']
            else:
                log_db("analyze_from_item", "FAIL",
                       message="GPT analyze fail", analyzed=analyzed)
                try:
                    return False, analyzed['tokens']
                except:
                    return False, 0
    except:
        error_message = traceback.format_exc()
        log_db("analyze_from_item", "ERROR", error=error_message)
        try:
            return False, analyzed['tokens']
        except:
            return False, 0
