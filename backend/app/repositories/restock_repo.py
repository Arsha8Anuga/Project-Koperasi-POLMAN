# app/repositories/restock_repo.py
from datetime import datetime
from app.utils.serialize import to_oid


async def find_page(db, supplier_id: str | None, start: datetime | None,
                    end: datetime | None, skip: int, limit: int):
    q = {"type": "RESTOCK"}
    if supplier_id:
        q["supplier.id"] = to_oid(supplier_id)
    if start or end:
        q["createdAt"] = {}
        if start:
            q["createdAt"]["$gte"] = start
        if end:
            q["createdAt"]["$lt"] = end          # batas atas eksklusif
    total = await db.transactions.count_documents(q)
    docs = await db.transactions.find(q).sort("createdAt", -1).skip(skip).limit(limit).to_list()
    return docs, total


async def find_by_id(db, id: str):
    return await db.transactions.find_one({"_id": to_oid(id), "type": "RESTOCK"})


async def count_since(db, start: datetime) -> int:
    return await db.transactions.count_documents(
        {"type": "RESTOCK", "createdAt": {"$gte": start}})