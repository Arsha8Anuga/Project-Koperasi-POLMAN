from typing import Any

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase

from app.repositories.base import find_page
from app.utils.pagination import PageParams


def _col(db: AsyncDatabase):
    return db["members"]


async def find_by_id(db: AsyncDatabase, member_id: ObjectId) -> dict[str, Any] | None:
    return await _col(db).find_one({"_id": member_id})


async def member_numbers_matching(db: AsyncDatabase, pattern: str) -> list[str]:
    """Semua memberNumber yang cocok regex (dipakai sekali untuk menyelaraskan counter)."""
    cursor = _col(db).find({"memberNumber": {"$regex": pattern}}, {"memberNumber": 1, "_id": 0})
    return [d["memberNumber"] async for d in cursor]


async def find_active_by_number(db: AsyncDatabase, member_number: str) -> dict[str, Any] | None:
    return await _col(db).find_one({"memberNumber": member_number, "isActive": True})


async def insert(db: AsyncDatabase, doc: dict[str, Any]) -> dict[str, Any]:
    result = await _col(db).insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


async def update(db: AsyncDatabase, member_id: ObjectId, fields: dict[str, Any]) -> dict[str, Any] | None:
    return await _col(db).find_one_and_update(
        {"_id": member_id}, {"$set": fields}, return_document=ReturnDocument.AFTER
    )


async def list_page(
    db: AsyncDatabase, filter: dict[str, Any], page: PageParams
) -> tuple[list[dict[str, Any]], int]:
    return await find_page(_col(db), filter, page, sort=[("memberNumber", 1), ("_id", 1)])


async def count_active(db: AsyncDatabase) -> int:
    return await _col(db).count_documents({"isActive": True})


async def find_active_by_id(db: AsyncDatabase, member_id: ObjectId) -> dict[str, Any] | None:
    return await _col(db).find_one({"_id": member_id, "isActive": True})
