"""Alur antrean end-to-end dengan MongoDB tiruan (mongomock)."""

import random
from datetime import UTC, datetime, timedelta

import mongomock
from bson import ObjectId

from engine.config import Settings
from engine.worker import tick


def make_db():
    db = mongomock.MongoClient(tz_aware=True)["koperasi_test_engine"]
    rng = random.Random(3)
    ids = {sku: ObjectId() for sku in ("MI", "TELUR", "AIR", "SABUN")}
    for sku, pid in ids.items():
        db.products.insert_one(
            {"_id": pid, "sku": sku, "name": f"Produk {sku}", "unit": "pcs", "stock": 30, "isActive": True}
        )
    now = datetime.now(UTC)
    for d in range(1, 60):
        for _ in range(8 + (6 if (now - timedelta(days=d)).weekday() >= 5 else 0)):
            items = [{"productId": ids["AIR"], "quantity": 1}]
            if rng.random() < 0.4:
                items = [{"productId": ids["MI"], "quantity": 2}]
                if rng.random() < 0.7:
                    items.append({"productId": ids["TELUR"], "quantity": 1})
            db.transactions.insert_one(
                {
                    "type": "SALE",
                    "status": "COMPLETED",
                    "createdAt": now - timedelta(days=d, hours=rng.randint(0, 8)),
                    "items": items,
                }
            )
    # telur sempat habis 3 hari lalu dan belum direstock
    db.stock_movements.insert_one({"productId": ids["TELUR"], "createdAt": now - timedelta(days=3), "stockAfter": 0})
    return db, ids


def test_tick_membuat_job_jadwal_dan_menulis_insights():
    db, ids = make_db()
    assert tick(db, Settings()) is True  # belum ada hasil → job SCHEDULE dibuat & diproses
    job = db.ai_jobs.find_one({})
    assert job["trigger"] == "SCHEDULE" and job["status"] == "DONE" and job["error"] is None
    assert db.ai_engine_status.find_one({"_id": "engine"})["lastSeenAt"] is not None

    rules = db.insights.find_one({"_id": "association_rules"})["rules"]
    mi_telur = next(r for r in rules if r["antecedent"][0]["sku"] == "MI" and r["consequent"][0]["sku"] == "TELUR")
    assert 0.6 < mi_telur["confidence"] < 0.8 and mi_telur["lift"] > 1.5

    fc = {p["sku"]: p for p in db.insights.find_one({"_id": "forecast"})["products"]}
    assert set(fc) == {"MI", "TELUR", "AIR", "SABUN"}
    assert fc["TELUR"]["excludedStockoutDays"] == 3  # hari-hari stok habis tidak dipakai melatih
    assert fc["SABUN"]["avgDaily"] == 0 and fc["SABUN"]["daysUntilStockout"] is None
    assert fc["MI"]["avgDaily"] > fc["AIR"]["avgDaily"] > 0  # MI 40% × 2 unit vs AIR 60% × 1 unit
    assert len(fc["AIR"]["forecast"]) == 14 and len(fc["AIR"]["history"]) == 28

    # hasil masih segar → putaran berikutnya tidak membuat job
    assert tick(db, Settings()) is False


def test_job_manual_diproses_dan_job_basi_digagalkan():
    db, _ = make_db()
    old = db.ai_jobs.insert_one(
        {
            "status": "RUNNING",
            "trigger": "MANUAL",
            "kinds": [],
            "requestedAt": datetime.now(UTC) - timedelta(hours=2),
            "startedAt": datetime.now(UTC) - timedelta(hours=2),
        }
    ).inserted_id
    manual = db.ai_jobs.insert_one(
        {"status": "PENDING", "trigger": "MANUAL", "kinds": ["association_rules"], "requestedAt": datetime.now(UTC)}
    ).inserted_id
    assert tick(db, Settings()) is True
    assert db.ai_jobs.find_one({"_id": old})["status"] == "FAILED"
    assert db.ai_jobs.find_one({"_id": manual})["status"] == "DONE"
    assert db.insights.find_one({"_id": "forecast"}) is None  # hanya jenis yang diminta


def test_koneksi_putus_sesaat_diulang(monkeypatch):
    from pymongo.errors import AutoReconnect

    from engine import worker

    db, _ = make_db()
    calls = {"n": 0}
    real_run = worker.run

    def flaky(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            raise AutoReconnect("operation cancelled")
        return real_run(*args, **kwargs)

    monkeypatch.setattr(worker, "run", flaky)
    job = worker.create_job(db, "MANUAL")
    job = worker.claim(db)
    waits = []
    assert worker.process(db, Settings(), job, sleep=waits.append) is True
    assert calls["n"] == 2 and waits == [5]
    assert db.ai_jobs.find_one({"_id": job["_id"]})["status"] == "DONE"


def test_koneksi_terus_putus_jadi_failed(monkeypatch):
    from pymongo.errors import AutoReconnect

    from engine import worker

    db, _ = make_db()
    monkeypatch.setattr(worker, "run", lambda *a, **k: (_ for _ in ()).throw(AutoReconnect("down")))
    worker.create_job(db, "MANUAL")
    job = worker.claim(db)
    waits = []
    assert worker.process(db, Settings(), job, sleep=waits.append) is False
    assert waits == [5, 15]
    doc = db.ai_jobs.find_one({"_id": job["_id"]})
    assert doc["status"] == "FAILED" and "terputus 3x" in doc["error"]
