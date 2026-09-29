from typing import Any

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase


def _col(db: AsyncDatabase):
    return db["categories"]


async def find_all(db: AsyncDatabase, filter: dict[str, Any]) -> list[dict[str, Any]]:
    return await _col(db).find(filter).sort([("name", 1), ("_id", 1)]).to_list()


async def find_by_id(db: AsyncDatabase, category_id: ObjectId) -> dict[str, Any] | None:
    return await _col(db).find_one({"_id": category_id})


async def name_map(db: AsyncDatabase) -> dict[ObjectId, str]:
    """{_id: name} semua kategori — untuk mengisi `categoryName` produk tanpa query per baris."""
    return {c["_id"]: c["name"] async for c in _col(db).find({}, {"name": 1})}


async def insert(db: AsyncDatabase, doc: dict[str, Any]) -> dict[str, Any]:
    doc["_id"] = (await _col(db).insert_one(doc)).inserted_id
    return doc


async def update(db: AsyncDatabase, category_id: ObjectId, fields: dict[str, Any]) -> dict[str, Any] | None:
    return await _col(db).find_one_and_update(
        {"_id": category_id}, {"$set": fields}, return_document=ReturnDocument.AFTER
    )
