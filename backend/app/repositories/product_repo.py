from typing import Any

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase

from app.repositories.base import Sort, find_page
from app.utils.pagination import PageParams

# Filter MongoDB per status stok. Harus sama persis dengan `stock_status()` di product_service.
STOCK_STATUS_FILTERS: dict[str, dict[str, Any]] = {
    "OUT": {"stock": {"$lte": 0}},
    "LOW": {"stock": {"$gt": 0}, "$expr": {"$lte": ["$stock", "$minimumStock"]}},
    "OK": {"stock": {"$gt": 0}, "$expr": {"$gt": ["$stock", "$minimumStock"]}},
}

SORT_OPTIONS: dict[str, Sort] = {
    "name": [("name", 1), ("_id", 1)],
    "stock": [("stock", 1), ("_id", 1)],
    "-stock": [("stock", -1), ("_id", -1)],
    "-createdAt": [("createdAt", -1), ("_id", -1)],
}


def _col(db: AsyncDatabase):
    return db["products"]


async def find_by_id(db: AsyncDatabase, product_id: ObjectId, session=None) -> dict[str, Any] | None:
    return await _col(db).find_one({"_id": product_id}, session=session)


async def find_one(db: AsyncDatabase, filter: dict[str, Any]) -> dict[str, Any] | None:
    return await _col(db).find_one(filter)


async def find_by_ids(db: AsyncDatabase, ids: list[ObjectId], session=None) -> list[dict[str, Any]]:
    return await _col(db).find({"_id": {"$in": ids}}, session=session).to_list()


async def find_all(db: AsyncDatabase, filter: dict[str, Any]) -> list[dict[str, Any]]:
    return await _col(db).find(filter).sort([("name", 1), ("_id", 1)]).to_list()


async def list_page(
    db: AsyncDatabase, filter: dict[str, Any], page: PageParams, sort: str
) -> tuple[list[dict[str, Any]], int]:
    return await find_page(_col(db), filter, page, sort=SORT_OPTIONS[sort])


async def count_by_stock_status(db: AsyncDatabase, filter: dict[str, Any]) -> dict[str, int]:
    counts = {"OK": 0, "LOW": 0, "OUT": 0}
    for status, cond in STOCK_STATUS_FILTERS.items():
        counts[status] = await _col(db).count_documents({**filter, **cond})
    return counts


async def insert(db: AsyncDatabase, doc: dict[str, Any]) -> dict[str, Any]:
    doc["_id"] = (await _col(db).insert_one(doc)).inserted_id
    return doc


async def update(
    db: AsyncDatabase, product_id: ObjectId, set_fields: dict[str, Any], unset_fields: list[str] | None = None
) -> dict[str, Any] | None:
    update: dict[str, Any] = {"$set": set_fields}
    if unset_fields:
        update["$unset"] = {f: "" for f in unset_fields}
    return await _col(db).find_one_and_update(
        {"_id": product_id}, update, return_document=ReturnDocument.AFTER
    )


async def decrement_stock_if_available(
    db: AsyncDatabase, product_id: ObjectId, quantity: int, now, session=None
) -> dict[str, Any] | None:
    """Kurangi stok HANYA jika produk aktif dan stok cukup (pengaman utama BR-02: stok tidak minus).
    Syarat tidak terpenuhi → tidak ada yang berubah, return None."""
    return await _col(db).find_one_and_update(
        {"_id": product_id, "isActive": True, "stock": {"$gte": quantity}},
        {"$inc": {"stock": -quantity}, "$set": {"updatedAt": now}},
        return_document=ReturnDocument.AFTER,
        session=session,
    )


async def apply_restock(
    db: AsyncDatabase, product_id: ObjectId, quantity: int, cost_price: int, purchase_price: int, now, session
) -> dict[str, Any] | None:
    return await _col(db).find_one_and_update(
        {"_id": product_id},
        {
            "$inc": {"stock": quantity},
            "$set": {"costPrice": cost_price, "lastPurchasePrice": purchase_price, "updatedAt": now},
        },
        return_document=ReturnDocument.AFTER,
        session=session,
    )
