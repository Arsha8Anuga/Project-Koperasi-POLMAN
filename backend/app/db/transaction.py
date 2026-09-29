"""Helper transaction MongoDB (butuh replica set). Dipakai checkout & restock.

    async def txn(session):
        await db.products.update_one(..., session=session)
        await audit.log(db, user, ..., session=session)
        return hasil

    hasil = await run_in_transaction(db.client, txn)

`with_transaction` otomatis mengulang saat transient error (write conflict) dan
me-rollback SEMUA tulisan kalau callback raise exception (termasuk AppError).
Konsekuensinya: callback bisa dijalankan lebih dari sekali, jadi jangan lakukan
efek samping di luar database di dalamnya.
"""

from collections.abc import Awaitable, Callable
from typing import TypeVar

from pymongo import AsyncMongoClient
from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.errors import DuplicateKeyError

T = TypeVar("T")

# Dua transaksi PERTAMA di hari yang sama bisa sama-sama meng-upsert dokumen counters
# (TRX-YYYYMMDD) dan salah satunya kena DuplicateKeyError. Aman untuk diulang.
_MAX_ATTEMPTS = 3


async def run_in_transaction(
    client: AsyncMongoClient, callback: Callable[[AsyncClientSession], Awaitable[T]]
) -> T:
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            async with client.start_session() as session:
                return await session.with_transaction(callback)
        except DuplicateKeyError:
            if attempt == _MAX_ATTEMPTS:
                raise
    raise RuntimeError("tidak terjangkau")
