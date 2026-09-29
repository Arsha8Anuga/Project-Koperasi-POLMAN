"""Fixture bersama. Test integration memakai MongoDB SUNGGUHAN (replica set), database
`TEST_MONGODB_DB` dari .env, yang SEMUA collection-nya dihapus di awal dan akhir setiap test.

    TEST_MONGODB_DB=koperasi_test_be1 pytest
"""

import os

os.environ.setdefault("JWT_SECRET", "test-secret-" + "x" * 40)

from collections.abc import AsyncIterator  # noqa: E402

import httpx  # noqa: E402
import pytest  # noqa: E402
from pymongo.asynchronous.database import AsyncDatabase  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.db import mongo  # noqa: E402
from app.db.indexes import ensure_indexes  # noqa: E402
from app.main import app  # noqa: E402
from app.utils.time import utcnow  # noqa: E402

DEFAULT_PASSWORD = "password123"
_HASH_CACHE: dict[str, str] = {}  # bcrypt lambat; hash yang sama dipakai ulang antar test


@pytest.fixture
async def db() -> AsyncIterator[AsyncDatabase]:
    settings = get_settings()
    name = settings.test_mongodb_db
    if name == settings.mongodb_db or "test" not in name:
        pytest.exit(f"TEST_MONGODB_DB='{name}' terlihat seperti DB kerja. Test men-DROP DB ini — batal.")
    await mongo.connect(settings.mongodb_uri, name)
    database = mongo.get_database()
    await _clear(database)
    await ensure_indexes(database)
    try:
        yield database
    finally:
        await _clear(database)
        await mongo.close()


async def _clear(database: AsyncDatabase) -> None:
    # Drop per collection, BUKAN dropDatabase: role `readWrite` tidak punya izin dropDatabase,
    # jadi user aplikasi yang hak aksesnya minimal tetap bisa menjalankan test.
    for name in await database.list_collection_names():
        if not name.startswith("system."):
            await database.drop_collection(name)


@pytest.fixture
async def client(db) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app, client=("10.0.0.7", 12345))
    async with httpx.AsyncClient(transport=transport, base_url="http://test/api/v1") as c:
        yield c


async def make_user(
    db: AsyncDatabase,
    username: str,
    role: str,
    *,
    password: str = DEFAULT_PASSWORD,
    active: bool = True,
    name: str | None = None,
) -> dict:
    if password not in _HASH_CACHE:
        _HASH_CACHE[password] = hash_password(password)
    now = utcnow()
    doc = {
        "name": name or username.title(),
        "username": username,
        "passwordHash": _HASH_CACHE[password],
        "role": role,
        "isActive": active,
        "createdAt": now,
        "updatedAt": now,
    }
    doc["_id"] = (await db.users.insert_one(doc)).inserted_id
    return doc


async def login(client: httpx.AsyncClient, username: str, app_name: str, password: str = DEFAULT_PASSWORD):
    return await client.post(
        "/auth/login", json={"username": username, "password": password, "app": app_name}
    )


async def auth_header(client: httpx.AsyncClient, username: str, app_name: str = "ADMIN") -> dict[str, str]:
    res = await login(client, username, app_name)
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['data']['token']}"}


@pytest.fixture
async def admin(db, client):
    """User ADMIN + header token-nya."""
    user = await make_user(db, "admin", "ADMIN", name="Ani Admin")
    return user, await auth_header(client, "admin")


def assert_error(res: httpx.Response, status: int, code: str) -> dict:
    assert res.status_code == status, res.text
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == code
    assert isinstance(body["message"], str) and body["message"]
    return body


@pytest.fixture
async def staff(db, client) -> dict[str, dict[str, str]]:
    """Header token untuk tiap role: staff["KASIR"], staff["LOGISTIK"], dst. (+ "KASIR2")."""
    headers: dict[str, dict[str, str]] = {}
    for username, role, app_name in [
        ("admin", "ADMIN", "ADMIN"),
        ("owner", "OWNER", "ADMIN"),
        ("logistik", "LOGISTIK", "ADMIN"),
        ("kasir1", "KASIR", "KASIR"),
        ("kasir2", "KASIR", "KASIR"),
    ]:
        await make_user(db, username, role, name=username.title())
        key = "KASIR2" if username == "kasir2" else role
        headers[key] = await auth_header(client, username, app_name)
    return headers
