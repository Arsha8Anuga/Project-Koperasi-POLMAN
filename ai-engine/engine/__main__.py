"""python -m engine          → worker (loop terus, dipakai container)
python -m engine --once   → hitung sekali sekarang lalu keluar (uji manual)
"""

from __future__ import annotations

import argparse
import logging
import os

from pymongo import MongoClient

from engine.config import Settings, load_env_files, uri_problem
from engine.worker import claim, create_job, heartbeat, loop, process


def main() -> None:
    parser = argparse.ArgumentParser(description="AI engine Toko Koperasi")
    parser.add_argument("--once", action="store_true", help="hitung sekali lalu keluar")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    had_uri = "MONGODB_URI" in os.environ
    env_file = load_env_files()
    settings = Settings()
    source = "environment variable" if had_uri else (str(env_file) if env_file else "nilai bawaan (localhost)")
    problem = uri_problem(settings.mongodb_uri)
    if problem:
        hint = (
            " Hapus variabelnya (PowerShell: Remove-Item Env:MONGODB_URI) supaya backend/.env yang dipakai."
            if had_uri
            else ""
        )
        raise SystemExit(f"Konfigurasi salah: {problem}. Sumber: {source}.{hint}")
    logging.getLogger("engine").info("Konfigurasi dari %s, database %s", source, settings.mongodb_db)
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
