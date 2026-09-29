"""Query collection transactions (SALE dan RESTOCK ada di collection yang sama)."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from bson import ObjectId

from app.utils.mongo_ids import id_variants

# Pilihan urutan yang diizinkan untuk GET /transactions. _id dipakai sebagai pemisah
# agar urutan tetap stabil ketika ada nilai yang sama.
SORT_OPTIONS: dict[str, list[tuple[str, int]]] = {
    "createdAt": [("createdAt", 1), ("_id", 1)],
    "-createdAt": [("createdAt", -1), ("_id", -1)],
    "total": [("total", 1), ("_id", 1)],
    "-total": [("total", -1), ("_id", -1)],
}


async def insert(db, doc: dict, session=None) -> None:
    await db.transactions.insert_one(doc, session=session)


async def find_by_id(db, transaction_id: ObjectId, session=None) -> dict | None:
    return await db.transactions.find_one({"_id": transaction_id}, session=session)


def build_filter(
    *,
    tx_type: str | None = None,
    start_utc: datetime | None = None,
    end_utc: datetime | None = None,
    cashier_id: ObjectId | None = None,
    supplier_id: ObjectId | None = None,
    member_id: ObjectId | None = None,
    search: str | None = None,
) -> dict[str, Any]:
    """Susun filter MongoDB. Batas waktu: start inklusif, end eksklusif."""
    flt: dict[str, Any] = {}
    if tx_type:
        flt["type"] = tx_type
    if start_utc or end_utc:
        created: dict[str, datetime] = {}
        if start_utc:
            created["$gte"] = start_utc
        if end_utc:
            created["$lt"] = end_utc
        flt["createdAt"] = created
    if cashier_id:
        flt["cashier.id"] = {"$in": id_variants(cashier_id)}
    if supplier_id:
        flt["supplier.id"] = {"$in": id_variants(supplier_id)}
    if member_id:
        flt["member.id"] = {"$in": id_variants(member_id)}
    if search and search.strip():
        pattern = re.escape(search.strip())
        flt["$or"] = [
            {"code": {"$regex": pattern, "$options": "i"}},
            {"customerName": {"$regex": pattern, "$options": "i"}},
        ]
    return flt


async def find_page(
    db, flt: dict, sort_key: str, skip: int, limit: int
) -> list[dict]:
    cursor = (
        db.transactions.find(flt)
        .sort(SORT_OPTIONS[sort_key])
        .skip(skip)
        .limit(limit)
    )
    return await cursor.to_list(length=limit)


async def count(db, flt: dict) -> int:
    return await db.transactions.count_documents(flt)


async def summarize(db, flt: dict) -> dict[str, int]:
    """Hitung jumlah transaksi, total penjualan, dan total restock untuk filter yang sama."""
    pipeline = [
        {"$match": flt},
        {"$group": {"_id": "$type", "count": {"$sum": 1}, "total": {"$sum": "$total"}}},
    ]
    cursor = await db.transactions.aggregate(pipeline)
    rows = await cursor.to_list(length=None)
    result = {"count": 0, "totalSales": 0, "totalRestock": 0}
    for row in rows:
        result["count"] += int(row["count"])
        if row["_id"] == "SALE":
            result["totalSales"] = int(row["total"])
        elif row["_id"] == "RESTOCK":
            result["totalRestock"] = int(row["total"])
    return result
