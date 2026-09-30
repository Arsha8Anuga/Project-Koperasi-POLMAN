"""Endpoint /insights: backend hanya membaca dokumen yang ditulis AI engine."""

from datetime import timedelta

from app.utils.time import utcnow
from tests.conftest import assert_error
from tests.integration.helpers import make_category, make_product, make_supplier, restock


def ref(pid: str, sku: str) -> dict:
    return {"productId": pid, "sku": sku, "name": f"Produk {sku}"}


async def seed_catalog(client, staff):
    lg = staff["LOGISTIK"]
    cat = await make_category(client, lg)
    ids = {sku: await make_product(client, lg, cat, sku) for sku in ("MI", "TELUR", "AIR", "KOPI", "HABIS")}
    sup = await make_supplier(client, lg)
    res = await restock(client, lg, sup, [(ids[s], 10, 1000) for s in ("MI", "TELUR", "AIR", "KOPI")])
    assert res.status_code == 201, res.text
    return ids


async def put_rules(db, ids):
    now = utcnow()
    rules = [
        {
            "antecedent": [ref(ids["MI"], "MI")],
            "consequent": [ref(ids["TELUR"], "TELUR")],
            "support": 0.08,
            "confidence": 0.6,
            "lift": 3.9,
            "count": 80,
        },
        {
            "antecedent": [ref(ids["MI"], "MI")],
            "consequent": [ref(ids["AIR"], "AIR")],
            "support": 0.04,
            "confidence": 0.3,
            "lift": 1.7,
            "count": 40,
        },
        {
            "antecedent": [ref(ids["MI"], "MI"), ref(ids["KOPI"], "KOPI")],
            "consequent": [ref(ids["HABIS"], "HABIS")],
            "support": 0.02,
            "confidence": 0.9,
            "lift": 5.0,
            "count": 20,
        },
        {
            "antecedent": [ref(ids["KOPI"], "KOPI")],
            "consequent": [ref(ids["MI"], "MI")],
            "support": 0.02,
            "confidence": 0.2,
            "lift": 0.8,
            "count": 20,
        },
    ]
    await db.insights.insert_one(
        {
            "_id": "association_rules",
            "kind": "association_rules",
            "generatedAt": now,
            "params": {"minSupport": 0.01},
            "stats": {"transactions": 1000},
            "rules": rules,
        }
    )


async def test_saran_kasir_dari_isi_keranjang(db, client, staff):
    ids = await seed_catalog(client, staff)
    kasir = staff["KASIR"]

    # belum ada hasil engine: kosong, bukan error
    res = await client.get("/insights/frequently-bought", headers=kasir, params={"productIds": ids["MI"]})
    assert res.status_code == 200 and res.json()["data"]["items"] == []

    await put_rules(db, ids)
    res = await client.get("/insights/frequently-bought", headers=kasir, params={"productIds": ids["MI"]})
    items = res.json()["data"]["items"]
    assert [i["product"]["sku"] for i in items] == ["TELUR", "AIR"]  # urut confidence
    assert items[0]["because"] == ["Produk MI"] and "costPrice" not in items[0]["product"]

    # yang sudah di keranjang tidak disarankan; produk stok 0 (HABIS) tidak disarankan walau confidence tinggi
    params = {"productIds": f"{ids['MI']},{ids['TELUR']},{ids['KOPI']}"}
    res = await client.get("/insights/frequently-bought", headers=kasir, params=params)
    assert [i["product"]["sku"] for i in res.json()["data"]["items"]] == ["AIR"]

    assert_error(await client.get("/insights/frequently-bought", headers=staff["ADMIN"]), 403, "FORBIDDEN")


async def test_rules_untuk_owner_dan_forecast_untuk_logistik(db, client, staff):
    ids = await seed_catalog(client, staff)
    await put_rules(db, ids)
    res = await client.get("/insights/association-rules", headers=staff["OWNER"], params={"minLift": 1})
    data = res.json()["data"]
    assert data["meta"]["stats"]["transactions"] == 1000
    assert all(r["lift"] >= 1 for r in data["rules"]) and len(data["rules"]) == 3
    assert_error(await client.get("/insights/association-rules", headers=staff["KASIR"]), 403, "FORBIDDEN")

    today = utcnow().date()
    product = {
        "productId": ids["MI"],
        "sku": "MI",
        "name": "Produk MI",
        "unit": "pcs",
        "stock": 10,
        "avgDaily": 4.2,
        "model": "holt_winters",
        "wape": 0.21,
        "baselineWape": 0.3,
        "daysUntilStockout": 2.4,
        "stockoutDate": (today + timedelta(days=2)).isoformat(),
        "suggestedQty": 40,
        "reorderNeeded": True,
        "safetyStock": 6,
        "excludedStockoutDays": 1,
        "history": [{"date": today.isoformat(), "qty": 5}],
        "forecast": [
            {"date": (today + timedelta(days=1)).isoformat(), "qty": 4.1, "lower": 2.0, "upper": 6.3}
        ],
    }
    other = {
        **product,
        "productId": ids["AIR"],
        "sku": "AIR",
        "name": "Produk AIR",
        "daysUntilStockout": None,
        "stockoutDate": None,
        "reorderNeeded": False,
    }
    await db.insights.insert_one(
        {
            "_id": "forecast",
            "kind": "forecast",
            "generatedAt": utcnow(),
            "params": {"horizonDays": 14},
            "stats": {},
            "products": [other, product],
        }
    )

    res = await client.get("/insights/forecast", headers=staff["LOGISTIK"])
    products = res.json()["data"]["products"]
    assert [p["sku"] for p in products] == ["MI", "AIR"]  # paling mendesak dulu
    assert "history" not in products[0]

    res = await client.get(f"/insights/forecast/{ids['MI']}", headers=staff["OWNER"])
    detail = res.json()["data"]["product"]
    assert detail["forecast"][0]["upper"] == 6.3 and detail["suggestedQty"] == 40
    assert_error(
        await client.get(f"/insights/forecast/{ids['KOPI']}", headers=staff["LOGISTIK"]), 404, "NOT_FOUND"
    )
    assert_error(await client.get("/insights/forecast", headers=staff["KASIR"]), 403, "FORBIDDEN")


async def test_hitung_ulang_hanya_admin_dan_tidak_menumpuk(db, client, staff):
    admin = staff["ADMIN"]
    assert_error(await client.post("/insights/jobs", headers=staff["OWNER"]), 403, "FORBIDDEN")

    res = await client.post("/insights/jobs", headers=admin)
    assert res.status_code == 201, res.text
    job = res.json()["data"]
    assert job["status"] == "PENDING" and job["trigger"] == "MANUAL" and job["requestedBy"]["role"] == "ADMIN"

    assert_error(await client.post("/insights/jobs", headers=admin), 409, "JOB_IN_PROGRESS")

    log = await db.audit_logs.find_one({"module": "AI"})
    assert log["action"] == "RECOMPUTE"

    res = await client.get("/insights/status", headers=staff["OWNER"])
    st = res.json()["data"]
    assert st["engine"]["online"] is False and st["activeJob"]["id"] == job["id"]
    assert [i["kind"] for i in st["insights"]] == ["association_rules", "forecast"]

    # engine mati di tengah proses → job RUNNING basi dianggap gagal, admin bisa minta lagi
    await db.ai_jobs.update_one(
        {}, {"$set": {"status": "RUNNING", "startedAt": utcnow() - timedelta(hours=1)}}
    )
    await db.ai_engine_status.insert_one(
        {"_id": "engine", "lastSeenAt": utcnow(), "version": "1.0", "intervalMinutes": 15}
    )
    res = await client.post("/insights/jobs", headers=admin)
    assert res.status_code == 201
    st = (await client.get("/insights/status", headers=admin)).json()["data"]
    assert st["engine"]["online"] is True
    assert [j["status"] for j in st["recentJobs"]] == ["PENDING", "FAILED"]
