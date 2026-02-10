import pymongo
from typing import Any
import sys
from pathlib import Path

# Fix path to ensure imports work from top-level directory
sys.path.append(str(Path(__file__).resolve().parents[1]))


from config.settings import Settings, settings
settings: Settings

def init():
    try:
        client: Any = pymongo.MongoClient(settings.MONGO_URI)
        db = client[settings.DB_NAME]

        colls = [settings.COLLECTION_TRUTH, settings.COLLECTION_TRACES]
        for c in colls:
            if c not in db.list_collection_names():
                db.create_collection(c)
                print(f"Provisioned: {c}")

        # Create unique index on file_hash and chunk_index pair for granular retrieval
        db[settings.COLLECTION_TRUTH].create_index(
            [("file_hash", pymongo.ASCENDING), ("chunk_index", pymongo.ASCENDING)],
            unique=True
        )
        print("Aletheia Memory initialized successfully.")
        
    except Exception as e:
        print(f"Initialization failed: {e}")

if __name__ == "__main__":
    init()