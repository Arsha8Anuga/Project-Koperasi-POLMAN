"""Akses collection counters (nomor urut kode transaksi per hari)."""

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
