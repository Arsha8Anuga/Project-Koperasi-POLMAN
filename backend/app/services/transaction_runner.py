"""Penjalan MongoDB transaction yang bisa dipakai ulang (checkout, restock, dan lainnya)."""

from __future__ import annotations

import inspect
from typing import Any, Awaitable, Callable

from pymongo.errors import DuplicateKeyError

MAX_ATTEMPTS = 3


async def run_in_transaction(db, callback: Callable[[Any], Awaitable[Any]]) -> Any:
    """Jalankan callback(session) di dalam satu transaction.

    - with_transaction otomatis mengulang saat ada transient error (misalnya write conflict)
      dan melakukan rollback jika callback melempar exception.
    - DuplicateKeyError diulang beberapa kali. Ini bisa terjadi bila dua transaksi pertama
      hari itu membuat dokumen counters yang sama pada saat bersamaan.
    """
    client = db.client
    last_error: DuplicateKeyError | None = None
    for _ in range(MAX_ATTEMPTS):
        try:
            # Pada beberapa versi PyMongo start_session() harus di-await, pada versi lain tidak.
            started = client.start_session()
            session = await started if inspect.isawaitable(started) else started
            async with session:
                return await session.with_transaction(callback)
        except DuplicateKeyError as exc:
            last_error = exc
    assert last_error is not None
    raise last_error
