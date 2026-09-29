"""Query collection lain yang dibutuhkan alur checkout.

Berisi akses ke products, members, dan stock_movements khusus untuk penjualan.
Kalau BE-2 sudah punya fungsi yang sama di repository produk, fungsi di sini boleh
dipindahkan ke sana. Yang penting update stok tetap bersyarat.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from bson import ObjectId
from pymongo import ReturnDocument


async def find_products_by_ids(db, product_ids: list[ObjectId], session=None) -> list[dict]:
    cursor = db.products.find({"_id": {"$in": product_ids}}, session=session)
    return await cursor.to_list(length=None)


async def find_product(db, product_id: ObjectId, session=None) -> dict | None:
    return await db.products.find_one({"_id": product_id}, session=session)


async def decrement_stock_if_available(
    db, product_id: ObjectId, quantity: int, now: datetime, session=None
) -> dict | None:
    """Kurangi stok hanya jika produk aktif dan stok cukup.

    Ini pengaman utama agar stok tidak negatif (BR-02). Jika syarat tidak terpenuhi, tidak ada
    dokumen yang berubah dan fungsi mengembalikan None. Jika berhasil, yang dikembalikan
    adalah dokumen produk sesudah stoknya berkurang.
    """
    return await db.products.find_one_and_update(
        {"_id": product_id, "isActive": True, "stock": {"$gte": quantity}},
        {"$inc": {"stock": -quantity}, "$set": {"updatedAt": now}},
        return_document=ReturnDocument.AFTER,
        session=session,
    )


async def find_active_member(db, member_id: ObjectId, session=None) -> dict | None:
    return await db.members.find_one({"_id": member_id, "isActive": True}, session=session)


async def insert_movements(db, movements: list[dict[str, Any]], session=None) -> None:
    if movements:
        await db.stock_movements.insert_many(movements, session=session)
