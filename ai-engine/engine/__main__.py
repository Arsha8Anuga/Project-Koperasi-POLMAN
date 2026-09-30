"""python -m engine          → worker (loop terus, dipakai container)
python -m engine --once   → hitung sekali sekarang lalu keluar (uji manual)
"""

from __future__ import annotations

import argparse
import logging

from pymongo import MongoClient

from engine.config import Settings
from engine.worker import claim, create_job, heartbeat, loop, process


def main() -> None:
    parser = argparse.ArgumentParser(description="AI engine Toko Koperasi")
    parser.add_argument("--once", action="store_true", help="hitung sekali lalu keluar")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    settings = Settings()
    client = MongoClient(settings.mongodb_uri, tz_aware=True, serverSelectionTimeoutMS=10000)
    db = client[settings.mongodb_db]
    try:
        if args.once:
            heartbeat(db, settings)
            create_job(db, "MANUAL")
            job = claim(db)
            ok = process(db, settings, job) if job else False
            raise SystemExit(0 if ok else 1)
        loop(db, settings)
    finally:
        client.close()


if __name__ == "__main__":
    main()
