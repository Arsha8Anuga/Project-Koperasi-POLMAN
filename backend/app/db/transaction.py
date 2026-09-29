"""Helper transaction MongoDB (butuh replica set). Dipakai checkout & restock.

    async def txn(session):
        await db.products.update_one(..., session=session)
        await audit.log(db, user, ..., session=session)
        return hasil

    hasil = await run_in_transaction(client, txn)

`with_transaction` otomatis mengulang saat transient error (write conflict) dan
me-rollback SEMUA tulisan kalau callback raise exception (termasuk AppError).
Konsekuensinya: callback bisa dijalankan lebih dari sekali, jadi jangan lakukan
efek samping di luar database (kirim notifikasi, dll.) di dalamnya.
"""

from collections.abc import Awaitable, Callable
from typing import TypeVar

from pymongo import AsyncMongoClient
from pymongo.asynchronous.client_session import AsyncClientSession

T = TypeVar("T")


async def run_in_transaction(
    client: AsyncMongoClient, callback: Callable[[AsyncClientSession], Awaitable[T]]
) -> T:
    async with client.start_session() as session:
        return await session.with_transaction(callback)
