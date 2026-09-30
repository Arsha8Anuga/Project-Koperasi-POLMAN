"""Akses collection counters (nomor urut kode transaksi per hari & nomor anggota)."""

from __future__ import annotations

from pymongo import ReturnDocument


async def increment(db, key: str, session=None) -> int:
    """Naikkan nomor urut untuk key tertentu (contoh: TRX-20260928) dan kembalikan nilai barunya.

    Operasi $inc dengan upsert bersifat atomik, jadi dua checkout bersamaan tidak akan
    mendapat nomor yang sama.
    """
    doc = await db.counters.find_one_and_update(
        {"_id": key},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
        session=session,
    )
    return int(doc["seq"])


async def ensure_at_least(db, key: str, value: int) -> None:
    """Pastikan seq untuk key minimal `value` (tidak pernah menurunkan). Atomik lewat $max."""
    await db.counters.update_one({"_id": key}, {"$max": {"seq": value}}, upsert=True)


async def exists(db, key: str) -> bool:
    return await db.counters.find_one({"_id": key}, {"_id": 1}) is not None
