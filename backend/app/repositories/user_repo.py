from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase

from app.repositories.base import find_page
from app.utils.pagination import PageParams


def _col(db: AsyncDatabase):
    return db["users"]


async def find_by_id(db: AsyncDatabase, user_id: ObjectId) -> dict[str, Any] | None:
    return await _col(db).find_one({"_id": user_id})


async def find_by_id_str(db: AsyncDatabase, user_id: str) -> dict[str, Any] | None:
    try:
        oid = ObjectId(user_id)
    except (InvalidId, TypeError):
        return None
    return await find_by_id(db, oid)


async def find_by_username(db: AsyncDatabase, username: str) -> dict[str, Any] | None:
    return await _col(db).find_one({"username": username})


async def insert(db: AsyncDatabase, doc: dict[str, Any]) -> dict[str, Any]:
    result = await _col(db).insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


async def update(db: AsyncDatabase, user_id: ObjectId, fields: dict[str, Any]) -> dict[str, Any] | None:
    return await _col(db).find_one_and_update(
        {"_id": user_id}, {"$set": fields}, return_document=ReturnDocument.AFTER
    )


async def list_page(
    db: AsyncDatabase, filter: dict[str, Any], page: PageParams
) -> tuple[list[dict[str, Any]], int]:
    return await find_page(_col(db), filter, page, sort=[("createdAt", -1), ("_id", -1)])


async def count_active_by_role(db: AsyncDatabase) -> dict[str, int]:
    cursor = await _col(db).aggregate(
        [{"$match": {"isActive": True}}, {"$group": {"_id": "$role", "n": {"$sum": 1}}}]
    )
    return {row["_id"]: row["n"] async for row in cursor}
