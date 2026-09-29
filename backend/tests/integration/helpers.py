"""Pembuat data master lewat API (bukan insert langsung), supaya ikut menguji endpoint-nya."""

import httpx


async def make_category(client: httpx.AsyncClient, h: dict, name: str = "ATK") -> str:
    res = await client.post("/categories", headers=h, json={"name": name, "description": f"Kategori {name}"})
    assert res.status_code == 201, res.text
    return res.json()["data"]["id"]


async def make_product(
    client: httpx.AsyncClient,
    h: dict,
    category_id: str,
    sku: str,
    price: int = 4000,
    minimum: int = 5,
    **extra,
) -> str:
    body = {
        "sku": sku,
        "name": f"Produk {sku}",
        "categoryId": category_id,
        "unit": "pcs",
        "sellingPrice": price,
        "minimumStock": minimum,
        **extra,
    }
    res = await client.post("/products", headers=h, json=body)
    assert res.status_code == 201, res.text
    return res.json()["data"]["id"]


async def make_supplier(client: httpx.AsyncClient, h: dict, code: str = "SUP-001") -> str:
    res = await client.post("/suppliers", headers=h, json={"supplierCode": code, "name": f"Supplier {code}"})
    assert res.status_code == 201, res.text
    return res.json()["data"]["id"]


async def restock(client: httpx.AsyncClient, h: dict, supplier_id: str, items: list[tuple[str, int, int]]):
    body = {
        "supplierId": supplier_id,
        "items": [{"productId": p, "quantity": q, "purchasePrice": c} for p, q, c in items],
    }
    return await client.post("/restocks", headers=h, json=body)


async def get_product(client: httpx.AsyncClient, h: dict, product_id: str) -> dict:
    res = await client.get(f"/products/{product_id}", headers=h)
    assert res.status_code == 200, res.text
    return res.json()["data"]
