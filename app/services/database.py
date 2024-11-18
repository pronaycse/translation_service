from pymongo import MongoClient
from datetime import datetime
import os

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "translation_service"
COLLECTION_NAME = "file_history"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


def save_file_history(session_id, file_name, translated_file, language, result):
    """Save file processing history to MongoDB."""
    collection.insert_one({
        "session_id": session_id,
        "file_name": file_name,
        "translated_file": translated_file,
        "language": language,
        "result": result,
        "created_at": datetime.utcnow()
    })


def get_file_history(session_id):
    """Fetch file processing history from MongoDB."""
    return list(collection.find({"session_id": session_id}, {"_id": 0}))
