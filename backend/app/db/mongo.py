"""Koneksi MongoDB (PyMongo Async API — BUKAN Motor). Satu client untuk seluruh aplikasi.

Router mengambilnya lewat dependency `get_db` / `get_client` di `app.api.deps`, bukan
memanggil fungsi di sini langsung, supaya test bisa menggantinya.
"""

from datetime import UTC

from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

_client: AsyncMongoClient | None = None
_db: AsyncDatabase | None = None


def create_client(uri: str) -> AsyncMongoClient:
    # tz_aware: datetime dari DB selalu aware UTC, jadi tidak ada bug "naive vs aware".
    return AsyncMongoClient(uri, tz_aware=True, tzinfo=UTC, serverSelectionTimeoutMS=5000)


async def connect(uri: str, db_name: str) -> None:
    global _client, _db
    _client = create_client(uri)
    _db = _client[db_name]


async def close() -> None:
    global _client, _db
    if _client is not None:
        await _client.close()
    _client, _db = None, None


def get_client() -> AsyncMongoClient:
    if _client is None:
        raise RuntimeError("MongoDB belum terkoneksi (lifespan belum jalan?)")
    return _client


def get_database() -> AsyncDatabase:
    if _db is None:
        raise RuntimeError("MongoDB belum terkoneksi (lifespan belum jalan?)")
    return _db
