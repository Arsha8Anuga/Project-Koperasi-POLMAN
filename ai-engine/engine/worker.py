"""Loop utama engine: denyut, ambil job dari antrean, jadwal otomatis.

Alur tiap putaran (tiap AI_POLL_SECONDS):
1. tulis denyut ke ai_engine_status (backend memakai ini untuk status online/offline)
2. job RUNNING yang terlalu lama (engine sebelumnya mati) → FAILED
3. kalau tidak ada job aktif dan hasil terakhir sudah lebih tua dari AI_INTERVAL_MINUTES
   → buat job SCHEDULE
4. ambil satu job PENDING secara atomik (find_one_and_update) → RUNNING → jalankan → DONE / FAILED
"""

from __future__ import annotations

import logging
import signal
import socket
import time
import traceback
from datetime import UTC, datetime, timedelta

from pymongo import ReturnDocument
from pymongo.errors import AutoReconnect

from engine import __version__
from engine.config import Settings
from engine.runner import COMPUTE, run

log = logging.getLogger("engine.worker")

STALE_RUNNING = timedelta(minutes=30)
# Koneksi ke MongoDB jarak jauh bisa putus sesaat (heartbeat timeout → pool di-reset → query yang sedang
# jalan dibatalkan: AutoReconnect / NetworkTimeout / _OperationCancelled). Perhitungan diulang dari awal.
NETWORK_RETRIES = 3
RETRY_BACKOFF_SECONDS = (5, 15)
ALL_KINDS = list(COMPUTE)


def now() -> datetime:
    return datetime.now(UTC)


def heartbeat(db, settings: Settings) -> None:
    db["ai_engine_status"].update_one(
        {"_id": "engine"},
        {
            "$set": {
                "lastSeenAt": now(),
                "version": __version__,
                "intervalMinutes": settings.interval_minutes,
                "host": socket.gethostname(),
            }
        },
        upsert=True,
    )


def fail_stale(db) -> None:
    db["ai_jobs"].update_many(
        {"status": "RUNNING", "startedAt": {"$lt": now() - STALE_RUNNING}},
        {"$set": {"status": "FAILED", "finishedAt": now(), "error": "Engine berhenti di tengah proses"}},
    )


def _as_utc(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def schedule_if_due(db, settings: Settings) -> None:
    if db["ai_jobs"].find_one({"status": {"$in": ["PENDING", "RUNNING"]}}):
        return
    latest = db["insights"].find_one({}, {"generatedAt": 1}, sort=[("generatedAt", 1)])  # yang paling basi
    missing = db["insights"].count_documents({"_id": {"$in": ALL_KINDS}}) < len(ALL_KINDS)
    due = (
        missing
        or latest is None
        or now() - _as_utc(latest["generatedAt"]) >= timedelta(minutes=settings.interval_minutes)
    )
    if due:
        create_job(db, "SCHEDULE")


def create_job(db, trigger: str, requested_by=None):
    return (
        db["ai_jobs"]
        .insert_one(
            {
                "status": "PENDING",
                "trigger": trigger,
                "kinds": ALL_KINDS,
                "requestedBy": requested_by,
                "requestedAt": now(),
                "startedAt": None,
                "finishedAt": None,
                "error": None,
                "summary": None,
            }
        )
        .inserted_id
    )


def claim(db):
    return db["ai_jobs"].find_one_and_update(
        {"status": "PENDING"},
        {"$set": {"status": "RUNNING", "startedAt": now()}},
        sort=[("requestedAt", 1)],
        return_document=ReturnDocument.AFTER,
    )


def process(db, settings: Settings, job, sleep=time.sleep) -> bool:
    kinds = [k for k in (job.get("kinds") or ALL_KINDS) if k in COMPUTE]
    log.info("Job %s (%s) mulai: %s", job["_id"], job.get("trigger"), kinds)
    for attempt in range(1, NETWORK_RETRIES + 1):
        try:
            summary = run(db, settings, kinds, job["_id"])
            break
        except AutoReconnect as exc:
            if attempt == NETWORK_RETRIES:
                return _fail(
                    db, job, f"Koneksi MongoDB terputus {attempt}x berturut-turut ({type(exc).__name__}: {exc})"
                )
            wait = RETRY_BACKOFF_SECONDS[min(attempt, len(RETRY_BACKOFF_SECONDS)) - 1]
            log.warning("Job %s: koneksi MongoDB terputus (%s), ulang %d detik lagi", job["_id"], exc, wait)
            sleep(wait)
        except Exception as exc:  # noqa: BLE001 - job gagal harus tercatat, engine tetap hidup
            log.error("Job %s gagal:\n%s", job["_id"], traceback.format_exc())
            return _fail(db, job, f"{type(exc).__name__}: {exc}")
    db["ai_jobs"].update_one({"_id": job["_id"]}, {"$set": {"status": "DONE", "finishedAt": now(), "summary": summary}})
    log.info("Job %s selesai", job["_id"])
    return True


def _fail(db, job, message: str) -> bool:
    log.error("Job %s gagal: %s", job["_id"], message)
    try:
        db["ai_jobs"].update_one(
            {"_id": job["_id"]}, {"$set": {"status": "FAILED", "finishedAt": now(), "error": message[:500]}}
        )
    except AutoReconnect:
        log.error("Status FAILED tidak bisa ditulis; job akan ditandai gagal otomatis setelah 30 menit")
    return False


def tick(db, settings: Settings) -> bool:
    """Satu putaran. True kalau ada job yang diproses."""
    heartbeat(db, settings)
    fail_stale(db)
    schedule_if_due(db, settings)
    job = claim(db)
    if job is None:
        return False
    process(db, settings, job)
    return True


def loop(db, settings: Settings) -> None:
    stopping = False

    def stop(*_):
        nonlocal stopping
        stopping = True
        log.info("Menerima sinyal berhenti, menyelesaikan putaran ini...")

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    log.info(
        "AI engine %s jalan: DB=%s, jadwal tiap %d menit, cek antrean tiap %d detik",
        __version__,
        settings.mongodb_db,
        settings.interval_minutes,
        settings.poll_seconds,
    )
    while not stopping:
        try:
            worked = tick(db, settings)
        except Exception:  # noqa: BLE001 - mis. koneksi Mongo putus sebentar: coba lagi nanti
            log.error("Putaran gagal:\n%s", traceback.format_exc())
            worked = False
        if not worked:
            for _ in range(settings.poll_seconds):
                if stopping:
                    break
                time.sleep(1)
