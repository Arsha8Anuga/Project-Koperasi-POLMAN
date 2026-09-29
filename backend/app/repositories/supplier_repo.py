from typing import Any

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase

from app.repositories.base import find_page
from app.utils.pagination import PageParams


def _col(db: AsyncDatabase):
    return db["suppliers"]


async def find_by_id(db: AsyncDatabase, supplier_id: ObjectId) -> dict[str, Any] | None:
    return await _col(db).find_one({"_id": supplier_id})


async def list_page(
    db: AsyncDatabase, filter: dict[str, Any], page: PageParams
) -> tuple[list[dict[str, Any]], int]:
    return await find_page(_col(db), filter, page, sort=[("supplierCode", 1), ("_id", 1)])


async def insert(db: AsyncDatabase, doc: dict[str, Any]) -> dict[str, Any]:
    doc["_id"] = (await _col(db).insert_one(doc)).inserted_id
    return doc


async def update(db: AsyncDatabase, supplier_id: ObjectId, fields: dict[str, Any]) -> dict[str, Any] | None:
    return await _col(db).find_one_and_update(
        {"_id": supplier_id}, {"$set": fields}, return_document=ReturnDocument.AFTER
    )
