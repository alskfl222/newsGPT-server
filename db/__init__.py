import os
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
col_count = db.count




