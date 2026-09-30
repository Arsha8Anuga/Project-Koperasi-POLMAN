"""Healthcheck container: sehat kalau denyut engine di ai_engine_status < 3 menit yang lalu."""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta

from pymongo import MongoClient

from engine.config import Settings


def main() -> int:
    s = Settings()
    try:
        with MongoClient(s.mongodb_uri, tz_aware=True, serverSelectionTimeoutMS=8000) as client:
            doc = client[s.mongodb_db]["ai_engine_status"].find_one({"_id": "engine"})
    except Exception as exc:  # noqa: BLE001
        print(f"mongo error: {exc}")
        return 1
    if not doc or datetime.now(UTC) - doc["lastSeenAt"] > timedelta(minutes=3):
        print("denyut engine basi")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
