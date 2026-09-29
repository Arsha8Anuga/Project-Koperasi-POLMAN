from tests.conftest import assert_error
from tests.integration.helpers import get_product, make_category, make_product, make_supplier


async def test_kategori_crud_dan_rbac(db, client, staff):
    lg = staff["LOGISTIK"]
    cat_id = await make_category(client, lg, "ATK")
    assert_error(await client.post("/categories", headers=lg, json={"name": "ATK"}), 409, "DUPLICATE")
    assert_error(
        await client.post("/categories", headers=staff["KASIR"], json={"name": "X"}), 403, "FORBIDDEN"
    )
    assert_error(await client.get("/categories", headers=staff["ADMIN"]), 403, "FORBIDDEN")

    res = await client.put(
        f"/categories/{cat_id}",
        headers=lg,
        json={"name": "ATK", "description": "Alat tulis", "isActive": False},
    )
    assert res.status_code == 200 and res.json()["data"]["isActive"] is False
    res = await client.get("/categories", headers=staff["KASIR"], params={"isActive": "true"})
    assert res.json()["data"] == []
    actions = sorted([lg["action"] async for lg in db.audit_logs.find({"module": "CATEGORY"})])
    assert actions == ["CREATE", "DEACTIVATE", "UPDATE"]


async def test_produk_baru_mulai_nol_dan_field_stok_diabaikan(db, client, staff):
    lg = staff["LOGISTIK"]
    cat = await make_category(client, lg)
    res = await client.post(
        "/products",
        headers=lg,
        json={
            "sku": "atk-001",
            "name": "Buku",
            "categoryId": cat,
            "unit": "pcs",
            "sellingPrice": 4000,
            "stock": 999,
            "costPrice": 1,
        },
    )
    assert res.status_code == 201, res.text
    p = res.json()["data"]
    assert p["sku"] == "ATK-001" and p["stock"] == 0 and p["costPrice"] == 0
    assert p["categoryName"] == "ATK" and p["stockStatus"] == "OUT" and p["createdAt"].endswith("Z")


async def test_produk_validasi_dan_duplikat(db, client, staff):
    lg = staff["LOGISTIK"]
    cat = await make_category(client, lg)
    await make_product(client, lg, cat, "A-1", barcode="899001")
    # dua produk TANPA barcode harus boleh (bug index sparse yang lama)
    await make_product(client, lg, cat, "A-2")
    await make_product(client, lg, cat, "A-3", barcode="")
    body = {"sku": "A-1", "name": "X", "categoryId": cat, "unit": "pcs", "sellingPrice": 1}
    res = assert_error(await client.post("/products", headers=lg, json=body), 409, "DUPLICATE")
    assert res["error"]["details"][0]["field"] == "sku"
    res = assert_error(
        await client.post("/products", headers=lg, json={**body, "sku": "A-9", "barcode": "899001"}),
        409,
        "DUPLICATE",
    )
    assert res["error"]["details"][0]["field"] == "barcode"
    assert_error(
        await client.post("/products", headers=lg, json={**body, "sku": "A-8", "sellingPrice": 4000.5}),
        422,
        "VALIDATION_ERROR",
    )
    assert_error(
        await client.post("/products", headers=lg, json={**body, "sku": "A-8", "categoryId": "ngawur"}),
        422,
        "VALIDATION_ERROR",
    )


async def test_kasir_tidak_melihat_harga_pokok_dan_produk_nonaktif(db, client, staff):
    lg, ks = staff["LOGISTIK"], staff["KASIR"]
    cat = await make_category(client, lg)
    aktif = await make_product(client, lg, cat, "A-1")
    mati = await make_product(client, lg, cat, "A-2")
    await client.patch(f"/products/{mati}/status", headers=lg, json={"isActive": False})

    res = await client.get("/products", headers=ks, params={"isActive": "false"})  # dipaksa true
    data = res.json()["data"]
    assert [p["id"] for p in data] == [aktif]
    assert "costPrice" not in data[0] and "lastPurchasePrice" not in data[0]
    assert_error(await client.get(f"/products/{mati}", headers=ks), 404, "NOT_FOUND")

    res = await client.get("/products", headers=staff["OWNER"])
    assert res.json()["meta"]["total"] == 2 and "costPrice" in res.json()["data"][0]


async def test_update_produk_mencatat_perubahan_harga(db, client, staff):
    lg = staff["LOGISTIK"]
    cat = await make_category(client, lg)
    pid = await make_product(client, lg, cat, "A-1", price=4000, barcode="111")
    res = await client.put(
        f"/products/{pid}",
        headers=lg,
        json={
            "sku": "A-1",
            "name": "Produk A-1",
            "categoryId": cat,
            "unit": "pcs",
            "sellingPrice": 4500,
            "minimumStock": 5,
            "stock": 50,
        },
    )
    assert res.status_code == 200, res.text
    p = res.json()["data"]
    assert p["sellingPrice"] == 4500 and p["stock"] == 0 and p["barcode"] is None
    log = await db.audit_logs.find_one({"module": "PRODUCT", "description": {"$regex": "harga jual"}})
    assert "dari 4000 menjadi 4500" in log["description"]


async def test_filter_search_dan_status_stok(db, client, staff):
    lg = staff["LOGISTIK"]
    cat = await make_category(client, lg)
    ids = {sku: await make_product(client, lg, cat, sku, minimum=5) for sku in ("KOPI-1", "TEH-1", "GULA-1")}
    await db.products.update_one({"_id": __import__("bson").ObjectId(ids["KOPI-1"])}, {"$set": {"stock": 3}})
    await db.products.update_one({"_id": __import__("bson").ObjectId(ids["TEH-1"])}, {"$set": {"stock": 20}})

    async def skus(**params):
        res = await client.get("/products", headers=lg, params=params)
        assert res.status_code == 200, res.text
        return sorted(p["sku"] for p in res.json()["data"])

    assert await skus(stockStatus="LOW") == ["KOPI-1"]
    assert await skus(stockStatus="OK") == ["TEH-1"]
    assert await skus(stockStatus="OUT") == ["GULA-1"]
    assert await skus(search="kop") == ["KOPI-1"]
    assert (await get_product(client, lg, ids["KOPI-1"]))["stockStatus"] == "LOW"


async def test_supplier_crud(db, client, staff):
    lg = staff["LOGISTIK"]
    sid = await make_supplier(client, lg, "sup-001")
    assert_error(
        await client.post("/suppliers", headers=lg, json={"supplierCode": "SUP-001", "name": "X"}),
        409,
        "DUPLICATE",
    )
    res = await client.get("/suppliers", headers=staff["OWNER"], params={"search": "sup"})
    assert res.json()["meta"]["total"] == 1 and res.json()["data"][0]["supplierCode"] == "SUP-001"
    res = await client.patch(f"/suppliers/{sid}/status", headers=lg, json={"isActive": False})
    assert res.json()["data"]["isActive"] is False
    assert_error(
        await client.post("/suppliers", headers=staff["OWNER"], json={"supplierCode": "Z", "name": "Z"}),
        403,
        "FORBIDDEN",
    )
