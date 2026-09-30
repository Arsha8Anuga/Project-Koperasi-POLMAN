"""Akses collection insights, ai_jobs, dan ai_engine_status (ditulis oleh AI engine)."""

from datetime import datetime
from typing import Any

from pymongo import DESCENDING
from pymongo.asynchronous.database import AsyncDatabase

from app.core.enums import InsightKind, JobStatus

ACTIVE = [JobStatus.PENDING.value, JobStatus.RUNNING.value]


async def get_insight(db: AsyncDatabase, kind: InsightKind) -> dict[str, Any] | None:
    return await db["insights"].find_one({"_id": kind.value})


async def insight_meta(db: AsyncDatabase, kind: InsightKind) -> dict[str, Any] | None:
    """Hanya generatedAt/params/stats, tanpa isi besar (rules/products)."""
    return await db["insights"].find_one({"_id": kind.value}, {"generatedAt": 1, "params": 1, "stats": 1})


async def find_active_job(db: AsyncDatabase) -> dict[str, Any] | None:
    return await db["ai_jobs"].find_one({"status": {"$in": ACTIVE}}, sort=[("requestedAt", DESCENDING)])


async def insert_job(db: AsyncDatabase, doc: dict[str, Any]) -> dict[str, Any]:
    result = await db["ai_jobs"].insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


async def recent_jobs(db: AsyncDatabase, limit: int = 10) -> list[dict[str, Any]]:
    return await db["ai_jobs"].find({}).sort("requestedAt", DESCENDING).limit(limit).to_list()


async def fail_stale_running(db: AsyncDatabase, started_before: datetime, now: datetime) -> None:
    """Job RUNNING terlalu lama = engine mati di tengah jalan; tandai gagal agar antrean tidak macet."""
    await db["ai_jobs"].update_many(
        {"status": JobStatus.RUNNING.value, "startedAt": {"$lt": started_before}},
        {
            "$set": {
                "status": JobStatus.FAILED.value,
                "finishedAt": now,
                "error": "Engine berhenti di tengah proses",
            }
        },
    )


async def engine_status(db: AsyncDatabase) -> dict[str, Any] | None:
    return await db["ai_engine_status"].find_one({"_id": "engine"})
