from datetime import datetime
from app.utils.serialize import to_oid


async def find_page(db, product_id: str | None, type_: str | None,
                    start: datetime | None, end: datetime | None,
                    skip: int, limit: int):
    q = {}
    if product_id:
        q["productId"] = to_oid(product_id)
    if type_:
        q["type"] = type_
    if start or end:
        q["createdAt"] = {}
        if start:
            q["createdAt"]["$gte"] = start
        if end:
            q["createdAt"]["$lt"] = end          # batas atas eksklusif
    total = await db.stock_movements.count_documents(q)
    docs = await db.stock_movements.find(q).sort("createdAt", -1).skip(skip).limit(limit).to_list()
    return docs, total