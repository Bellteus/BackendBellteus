from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def get_mongo_client():
    MONGO_URI = os.getenv("MONGO_URI")
    if not MONGO_URI:
        raise Exception("No MONGO_URI configurado")
    client = MongoClient(MONGO_URI)
    return client
