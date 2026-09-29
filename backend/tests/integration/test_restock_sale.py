"""Test minimum dokumen 05 §10: restock + HPP, checkout, stok kurang, uang kurang, total manipulasi, RBAC."""

from tests.conftest import assert_error
from tests.integration.helpers import get_product, make_category, make_product, make_supplier, restock


async def _setup(client, staff, stock_a=50, stock_b=5):
    lg = staff["LOGISTIK"]
    cat = await make_category(client, lg)
    a = await make_product(client, lg, cat, "A-1", price=4000)
    b = await make_product(client, lg, cat, "B-1", price=2500)
    sup = await make_supplier(client, lg)
    res = await restock(client, lg, sup, [(a, stock_a, 3000), (b, stock_b, 1500)])
    assert res.status_code == 201, res.text
    return a, b, sup


async def test_restock_menambah_stok_dan_hpp_moving_average(db, client, staff):
    lg = staff["LOGISTIK"]
    a, b, sup = await _setup(client, staff)
    res = await restock(client, lg, sup, [(a, 100, 3200)])
    assert res.status_code == 201
    trx = res.json()["data"]
    assert trx["type"] == "RESTOCK" and trx["code"].startswith("RST-") and trx["code"].endswith("-0002")
    assert trx["total"] == 320000 and trx["items"][0]["purchasePrice"] == 3200 and trx["payment"] is None

    p = await get_product(client, lg, a)
    assert (
        p["stock"] == 150 and p["costPrice"] == 3133 and p["lastPurchasePrice"] == 3200
    )  # contoh dokumen 05

    res = await client.get("/stock/movements", headers=lg, params={"productId": a})
    moves = res.json()["data"]
    assert [m["quantity"] for m in moves] == [100, 50]
    assert moves[0]["stockBefore"] == 50 and moves[0]["stockAfter"] == 150


async def test_restock_validasi(db, client, staff):
    lg = staff["LOGISTIK"]
    a, _, sup = await _setup(client, staff)
    assert_error(await restock(client, lg, sup, [(a, 1, 1), (a, 2, 1)]), 400, "BAD_REQUEST")
    assert_error(await restock(client, lg, sup, [(a, 0, 1)]), 422, "VALIDATION_ERROR")
    assert_error(await restock(client, lg, sup, [("66f7a1b2c3d4e5f607182930", 1, 1)]), 404, "NOT_FOUND")
    await client.patch(f"/suppliers/{sup}/status", headers=lg, json={"isActive": False})
    assert_error(await restock(client, lg, sup, [(a, 1, 1)]), 400, "BAD_REQUEST")


async def test_checkout_sukses(db, client, staff):
    a, b, _ = await _setup(client, staff)
    ks = staff["KASIR"]
    res = await client.post(
        "/sales",
        headers=ks,
        json={
            "items": [{"productId": a, "quantity": 2}, {"productId": b, "quantity": 1}],
            "payment": {"method": "CASH", "amountPaid": 20000},
            "total": 1,
            "price": 1,
        },
    )  # total dari client harus diabaikan
    assert res.status_code == 201, res.text
    sale = res.json()["data"]
    assert sale["code"].startswith("TRX-") and sale["code"].endswith("-0001")
    assert sale["total"] == 2 * 4000 + 2500 and sale["payment"]["change"] == 20000 - 10500
    assert "costPrice" not in sale["items"][0]  # KASIR tidak menerima HPP

    lg = staff["LOGISTIK"]
    assert (await get_product(client, lg, a))["stock"] == 48
    assert (await get_product(client, lg, b))["stock"] == 4
    assert await db.stock_movements.count_documents({"type": "SALE"}) == 2
    assert await db.audit_logs.count_documents({"action": "SALE"}) == 1


async def test_stok_kurang_tidak_mengubah_apa_pun(db, client, staff):
    a, b, _ = await _setup(client, staff, stock_a=50, stock_b=5)
    res = await client.post(
        "/sales",
        headers=staff["KASIR"],
        json={
            "items": [{"productId": a, "quantity": 2}, {"productId": b, "quantity": 6}],
            "payment": {"method": "QRIS"},
        },
    )
    body = assert_error(res, 409, "INSUFFICIENT_STOCK")
    assert body["error"]["details"][0] == {
        "field": "items[1].quantity",
        "productId": b,
        "name": "Produk B-1",
        "requested": 6,
        "available": 5,
    }
    lg = staff["LOGISTIK"]
    assert (await get_product(client, lg, a))["stock"] == 50  # item pertama TIDAK ikut terpotong
    assert await db.transactions.count_documents({"type": "SALE"}) == 0
    assert await db.stock_movements.count_documents({"type": "SALE"}) == 0


async def test_rollback_saat_stok_berubah_di_tengah_transaksi(db, client, staff, monkeypatch):
    """Pre-check lolos, tapi update bersyarat item kedua gagal → item pertama harus di-rollback."""
    from app.services import sale_service

    a, b, _ = await _setup(client, staff, stock_a=50, stock_b=5)
    monkeypatch.setattr(sale_service, "check_products", lambda *a_, **k: None)
    await db.products.update_one({"sku": "B-1"}, {"$set": {"stock": 0}})
    res = await client.post(
        "/sales",
        headers=staff["KASIR"],
        json={
            "items": [{"productId": a, "quantity": 2}, {"productId": b, "quantity": 1}],
            "payment": {"method": "QRIS"},
        },
    )
    assert_error(res, 409, "INSUFFICIENT_STOCK")
    assert (await get_product(client, staff["LOGISTIK"], a))["stock"] == 50


async def test_pembayaran(db, client, staff):
    a, _, _ = await _setup(client, staff)
    ks = staff["KASIR"]
    res = await client.post(
        "/sales",
        headers=ks,
        json={"items": [{"productId": a, "quantity": 1}], "payment": {"method": "CASH", "amountPaid": 3999}},
    )
    assert_error(res, 422, "PAYMENT_INSUFFICIENT")
    res = await client.post(
        "/sales",
        headers=ks,
        json={"items": [{"productId": a, "quantity": 1}], "payment": {"method": "QRIS", "amountPaid": 1}},
    )
    assert res.status_code == 201
    assert res.json()["data"]["payment"] | {"paidAt": None} == {
        "method": "QRIS",
        "amountPaid": 4000,
        "change": 0,
        "paidAt": None,
    }


async def test_kasir_hanya_boleh_membuka_transaksinya_sendiri(db, client, staff):
    a, _, _ = await _setup(client, staff)
    res = await client.post(
        "/sales",
        headers=staff["KASIR"],
        json={"items": [{"productId": a, "quantity": 1}], "payment": {"method": "QRIS"}},
    )
    sale_id = res.json()["data"]["id"]
    assert (await client.get(f"/sales/{sale_id}", headers=staff["KASIR"])).status_code == 200
    assert_error(await client.get(f"/sales/{sale_id}", headers=staff["KASIR2"]), 403, "FORBIDDEN")
    res = await client.get(f"/sales/{sale_id}", headers=staff["OWNER"])
    assert "costPrice" in res.json()["data"]["items"][0]
    res = await client.get("/sales/mine", headers=staff["KASIR2"])
    assert res.json()["meta"]["total"] == 0


async def test_riwayat_owner_dan_summary(db, client, staff):
    a, _, _ = await _setup(client, staff)
    await client.post(
        "/sales",
        headers=staff["KASIR"],
        json={"items": [{"productId": a, "quantity": 2}], "payment": {"method": "QRIS"}},
    )
    res = await client.get("/transactions", headers=staff["OWNER"])
    body = res.json()
    assert body["meta"]["total"] == 2
    assert body["summary"] == {"count": 2, "totalSales": 8000, "totalRestock": 50 * 3000 + 5 * 1500}
    res = await client.get("/transactions", headers=staff["OWNER"], params={"type": "SALE", "search": "trx"})
    assert res.json()["meta"]["total"] == 1


async def test_laporan_stok_dan_dashboard_logistik(db, client, staff):
    lg = staff["LOGISTIK"]
    await _setup(client, staff, stock_a=50, stock_b=5)  # B-1: 5 <= minimum 5 → LOW
    res = await client.get("/reports/stock", headers=lg)
    assert res.json()["data"]["counts"] == {"OK": 1, "LOW": 1, "OUT": 0}
    res = await client.get("/reports/stock", headers=lg, params={"stockStatus": "LOW"})
    assert [i["sku"] for i in res.json()["data"]["items"]] == ["B-1"]
    res = await client.get("/dashboard/summary", headers=lg)
    assert res.json()["data"] == {
        "activeProducts": 2,
        "lowStockCount": 1,
        "outOfStockCount": 0,
        "restocksThisMonth": 1,
    }


async def test_rbac_dokumen_05(db, client, staff):
    assert_error(await client.post("/restocks", headers=staff["KASIR"], json={}), 403, "FORBIDDEN")
    assert_error(await client.get("/reports/cashflow", headers=staff["LOGISTIK"]), 403, "FORBIDDEN")
    assert_error(await client.get("/transactions", headers=staff["LOGISTIK"]), 403, "FORBIDDEN")
    assert_error(await client.post("/sales", headers=staff["OWNER"], json={}), 403, "FORBIDDEN")
    assert_error(await client.get("/stock/movements", headers=staff["KASIR"]), 403, "FORBIDDEN")
    assert_error(await client.post("/products", headers=staff["OWNER"], json={}), 403, "FORBIDDEN")
