from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL)

# Check connection
try:
    client.admin.command('ping')
    print("MongoDB Connected ✅")
except Exception as e:
    print("MongoDB Connection Error ❌", e)

db = client["notes_db"]
collection = db["notes"]

# Optional index (performance)
collection.create_index("created_at")