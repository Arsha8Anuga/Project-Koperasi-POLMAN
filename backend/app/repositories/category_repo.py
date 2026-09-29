from pymongo import ReturnDocument
from app.utils.serialize import to_oid

async def find_all(db, is_active: bool | None):
    q = {} if is_active is None else {"isActive": is_active}
    return await db.categories.find(q).sort("name", 1).to_list()

async def find_by_id(db, id: str):
    return await db.categories.find_one({"_id": to_oid(id)})

async def insert(db, doc: dict):
    res = await db.categories.insert_one(doc)
    doc["_id"] = res.inserted_id
    return doc

async def update(db, id: str, fields: dict):
    return await db.categories.find_one_and_update(
        {"_id": to_oid(id)}, {"$set": fields}, return_document=ReturnDocument.AFTER)