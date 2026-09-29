from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from app.db import mongo


async def get_db() -> AsyncDatabase:
    return mongo.get_database()


async def get_client() -> AsyncMongoClient:
    """Dibutuhkan untuk transaction (`run_in_transaction(client, ...)`) — checkout & restock."""
    return mongo.get_client()
