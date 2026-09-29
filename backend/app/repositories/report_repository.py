"""Pipeline agregasi untuk laporan owner.

Pengelompokan waktu dilakukan di MongoDB dengan zona Asia/Jakarta. Kunci kelompok langsung
berupa label periode (contoh 2026-09-28, 2026-09, atau 2026) supaya cocok dengan format
response dokumen 04 bagian 7.12.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from bson import ObjectId

from app.utils.time import TZ_NAME

# Format label per granularity. Untuk minggu, labelnya adalah tanggal hari Senin.
PERIOD_FORMATS = {
    "day": "%Y-%m-%d",
    "week": "%Y-%m-%d",
    "month": "%Y-%m",
    "year": "%Y",
}


def _period_expression(granularity: str) -> dict[str, Any]:
    trunc: dict[str, Any] = {
        "date": "$createdAt",
        "unit": granularity,
        "timezone": TZ_NAME,
    }
    if granularity == "week":
        trunc["startOfWeek"] = "monday"
    return {
        "$dateToString": {
            "format": PERIOD_FORMATS[granularity],
            "date": {"$dateTrunc": trunc},
            "timezone": TZ_NAME,
        }
    }


async def _run(db, pipeline: list[dict]) -> list[dict]:
    cursor = await db.transactions.aggregate(pipeline)
    return await cursor.to_list(length=None)


async def cashflow_rows(db, start_utc: datetime, end_utc: datetime, granularity: str) -> list[dict]:
    """Arus kas: pemasukan (total SALE) dan pengeluaran (total RESTOCK) per periode."""
    pipeline = [
        {
            "$match": {
                "status": "COMPLETED",
                "type": {"$in": ["SALE", "RESTOCK"]},
                "createdAt": {"$gte": start_utc, "$lt": end_utc},
            }
        },
        {
            "$group": {
                "_id": _period_expression(granularity),
                "income": {"$sum": {"$cond": [{"$eq": ["$type", "SALE"]}, "$total", 0]}},
                "expense": {"$sum": {"$cond": [{"$eq": ["$type", "RESTOCK"]}, "$total", 0]}},
            }
        },
        {"$sort": {"_id": 1}},
    ]
    return await _run(db, pipeline)


async def gross_profit_rows(db, start_utc: datetime, end_utc: datetime, granularity: str) -> list[dict]:
    """Laba kotor: pendapatan (subtotal item) dan HPP (quantity x costPrice) per periode."""
    pipeline = [
        {
            "$match": {
                "status": "COMPLETED",
                "type": "SALE",
                "createdAt": {"$gte": start_utc, "$lt": end_utc},
            }
        },
        {"$unwind": "$items"},
        {
            "$group": {
                "_id": _period_expression(granularity),
                "revenue": {"$sum": "$items.subtotal"},
                "cogs": {
                    "$sum": {
                        "$multiply": [
                            "$items.quantity",
                            {"$ifNull": ["$items.costPrice", 0]},
                        ]
                    }
                },
            }
        },
        {"$sort": {"_id": 1}},
    ]
    return await _run(db, pipeline)


async def find_product_ids_by_category(db, category_id: ObjectId) -> list[ObjectId | str]:
    """Ambil id semua produk dalam satu kategori (untuk filter best seller)."""
    cursor = db.products.find({"categoryId": category_id}, {"_id": 1})
    docs = await cursor.to_list(length=None)
    return [doc["_id"] for doc in docs]


async def best_seller_rows(
    db,
    start_utc: datetime,
    end_utc: datetime,
    limit: int,
    product_ids: list[ObjectId | str] | None = None,
) -> list[dict]:
    """Produk terlaris berdasarkan jumlah terjual, lalu pendapatan sebagai pemisah."""
    pipeline: list[dict[str, Any]] = [
        {
            "$match": {
                "status": "COMPLETED",
                "type": "SALE",
                "createdAt": {"$gte": start_utc, "$lt": end_utc},
            }
        },
        {"$unwind": "$items"},
    ]
    if product_ids is not None:
        pipeline.append({"$match": {"items.productId": {"$in": product_ids}}})
    pipeline.extend(
        [
            {
                "$group": {
                    "_id": "$items.productId",
                    "sku": {"$first": "$items.sku"},
                    "name": {"$first": "$items.name"},
                    "quantitySold": {"$sum": "$items.quantity"},
                    "revenue": {"$sum": "$items.subtotal"},
                }
            },
            {"$sort": {"quantitySold": -1, "revenue": -1, "_id": 1}},
            {"$limit": limit},
        ]
    )
    return await _run(db, pipeline)
