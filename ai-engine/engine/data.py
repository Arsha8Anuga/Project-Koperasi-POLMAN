"""Membaca data mentah dari MongoDB dan mengubahnya ke bentuk yang dipakai model."""

from __future__ import annotations

from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from typing import Any

import numpy as np

from engine.config import WIB


def to_wib_date(value: datetime) -> date:
    if value.tzinfo is None:  # PyMongo tanpa tz_aware / mongomock
        value = value.replace(tzinfo=UTC)
    return value.astimezone(WIB).date()


def wib_midnight_utc(d: date) -> datetime:
    return datetime(d.year, d.month, d.day, tzinfo=WIB).astimezone(UTC)


def load_baskets(db, since: datetime) -> list[set[str]]:
    """Satu set productId per transaksi penjualan (jumlah per item tidak dipakai di association rules)."""
    cursor = db["transactions"].find(
        {"type": "SALE", "status": "COMPLETED", "createdAt": {"$gte": since}}, {"items.productId": 1}
    )
    return [{str(i["productId"]) for i in doc.get("items", [])} for doc in cursor]


def load_products(db, active_only: bool = True) -> dict[str, dict[str, Any]]:
    query = {"isActive": True} if active_only else {}
    projection = {"sku": 1, "name": 1, "unit": 1, "stock": 1, "isActive": 1}
    return {str(p["_id"]): p for p in db["products"].find(query, projection)}


def daily_sales(db, first_day: date, last_day: date) -> dict[str, np.ndarray]:
    """Unit terjual per produk per hari WIB, first_day..last_day (inklusif)."""
    n = (last_day - first_day).days + 1
    series: dict[str, np.ndarray] = defaultdict(lambda: np.zeros(n))
    cursor = db["transactions"].find(
        {
            "type": "SALE",
            "status": "COMPLETED",
            "createdAt": {"$gte": wib_midnight_utc(first_day), "$lt": wib_midnight_utc(last_day + timedelta(days=1))},
        },
        {"createdAt": 1, "items.productId": 1, "items.quantity": 1},
    )
    for doc in cursor:
        day = (to_wib_date(doc["createdAt"]) - first_day).days
        if 0 <= day < n:
            for item in doc.get("items", []):
                series[str(item["productId"])][day] += item["quantity"]
    return dict(series)


def stockout_days(db, first_day: date, last_day: date) -> dict[str, set[int]]:
    """Indeks hari ketika produk sedang kehabisan stok (sejak stockAfter = 0 sampai restock berikutnya).

    Di hari-hari itu penjualan tercatat lebih rendah dari permintaan sebenarnya (barangnya tidak ada),
    jadi hari tersebut tidak dipakai untuk melatih model (data tersensor).
    """
    n = (last_day - first_day).days + 1
    result: dict[str, set[int]] = defaultdict(set)
    out_since: dict[str, int] = {}
    cursor = (
        db["stock_movements"]
        .find(
            {"createdAt": {"$gte": wib_midnight_utc(first_day), "$lt": wib_midnight_utc(last_day + timedelta(days=1))}},
            {"productId": 1, "createdAt": 1, "stockAfter": 1},
        )
        .sort("createdAt", 1)
    )
    for mv in cursor:
        pid = str(mv["productId"])
        day = (to_wib_date(mv["createdAt"]) - first_day).days
        if mv["stockAfter"] <= 0:
            out_since.setdefault(pid, day)
        elif pid in out_since:
            start = out_since.pop(pid)
            # hari restock sendiri tidak disensor (restock pagi, penjualan setelahnya normal)
            result[pid].update(range(start, max(start + 1, day)))
    for pid, start in out_since.items():  # masih habis sampai hari terakhir
        result[pid].update(range(start, n))
    return dict(result)
