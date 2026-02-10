import os
import sqlite3
from pymongo import MongoClient
from chromadb.client import Client as ChromaClient  # type: ignore

# === Customization Variables ===
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "./data/app.db")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DB = os.getenv("MONGODB_DB", "aletheia_db")
CHROMADB_PATH = os.getenv("CHROMADB_PATH", "./data/chromadb")

# === Health Check Logic ===

def check_sqlite_health():
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.execute("SELECT 1")
        conn.close()
        return True, "SQLite healthy"
    except Exception as e:
        return False, f"SQLite error: {e}"

def check_mongodb_health():
    try:
        client: MongoClient = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=2000)
        client.server_info()  # Will throw if cannot connect
        db = client[MONGODB_DB]
        db.list_collection_names()
        return True, "MongoDB healthy"
    except Exception as e:
        return False, f"MongoDB error: {e}"

def check_chromadb_health():
    try:
        client = ChromaClient(path=CHROMADB_PATH)
        _ = client.list_collections()
        return True, "ChromaDB healthy"
    except Exception as e:
        return False, f"ChromaDB error: {e}"

def system_health():
    health = {}
    sqlite_ok, sqlite_msg = check_sqlite_health()
    mongo_ok, mongo_msg = check_mongodb_health()
    chroma_ok, chroma_msg = check_chromadb_health()
    health["sqlite"] = {"ok": sqlite_ok, "msg": sqlite_msg}
    health["mongodb"] = {"ok": mongo_ok, "msg": mongo_msg}
    health["chromadb"] = {"ok": chroma_ok, "msg": chroma_msg}
    health["all_ok"] = sqlite_ok and mongo_ok and chroma_ok
    return health
