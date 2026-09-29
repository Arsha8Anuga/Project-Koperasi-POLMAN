import re
from pymongo import ReturnDocument
from app.utils.serialize import to_oid


def _build_query(search: str | None, is_active: bool | None) -> dict:
    q = {}
    if is_active is not None:
        q["isActive"] = is_active
    if search:
        rx = {"$regex": re.escape(search), "$options": "i"}
        q["$or"] = [{"name": rx}, {"supplierCode": rx}]
    return q


async def insert(db, doc: dict):
    res = await db.suppliers.insert_one(doc)
    doc["_id"] = res.inserted_id
    return doc


async def find_by_id(db, id: str):
    return await db.suppliers.find_one({"_id": to_oid(id)})


async def find_page(db, search, is_active, skip: int, limit: int):
    q = _build_query(search, is_active)
    total = await db.suppliers.count_documents(q)
    docs = await db.suppliers.find(q).sort("name", 1).skip(skip).limit(limit).to_list()
    return docs, total


async def update(db, id: str, fields: dict):
    return await db.suppliers.find_one_and_update(
        {"_id": to_oid(id)}, {"$set": fields}, return_document=ReturnDocument.AFTER)