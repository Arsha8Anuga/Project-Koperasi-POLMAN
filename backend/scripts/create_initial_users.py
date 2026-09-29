"""Membuat 1 user per role supaya tim bisa login. Idempoten: user yang sudah ada dilewati.

Jalankan dari folder backend/:
    python -m scripts.create_initial_users
    python -m scripts.create_initial_users --password rahasia-tim-123

Akun (password sama untuk semua, HANYA untuk dev/demo):
    owner / logistik / admin / kasir1
"""

import argparse
import asyncio

from app.core.config import get_settings
from app.core.security import hash_password
from app.db import mongo
from app.db.indexes import ensure_indexes
from app.utils.time import utcnow

USERS = [
    ("owner", "Oscar Owner", "OWNER"),
    ("logistik", "Rudi Logistik", "LOGISTIK"),
    ("admin", "Ani Admin", "ADMIN"),
    ("kasir1", "Siti Kasir", "KASIR"),
]


async def main(password: str) -> None:
    settings = get_settings()
    await mongo.connect(settings.mongodb_uri, settings.mongodb_db)
    db = mongo.get_database()
    try:
        await ensure_indexes(db)
        for username, name, role in USERS:
            if await db.users.find_one({"username": username}):
                print(f"  lewati  {username:<10} (sudah ada)")
                continue
            now = utcnow()
            await db.users.insert_one(
                {
                    "name": name,
                    "username": username,
                    "passwordHash": hash_password(password),
                    "role": role,
                    "isActive": True,
                    "createdAt": now,
                    "updatedAt": now,
                }
            )
            print(f"  dibuat  {username:<10} {role}")
        print(f"Database: {settings.mongodb_db} · password: {password}")
    finally:
        await mongo.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--password", default="koperasi123", help="minimal 8 karakter (default: koperasi123)")
    args = parser.parse_args()
    if len(args.password) < 8:
        parser.error("password minimal 8 karakter")
    asyncio.run(main(args.password))
