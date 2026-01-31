import os
from typing import Optional

from fastapi import HTTPException
from pymongo import MongoClient
from pymongo.database import Database


# MongoDB connection (lazy initialization for serverless)
_client: Optional[MongoClient] = None


def get_database() -> Database:
    global _client
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise HTTPException(status_code=503)
    if _client is None:
        _client = MongoClient(uri)
    return _client.carryon
