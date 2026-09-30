import pytest

from app.services import product_image_service
from tests.conftest import assert_error
from tests.integration.helpers import get_product, make_category, make_product

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 200
JPEG = b"\xff\xd8\xff\xe0" + b"\x01" * 300
WEBP = b"RIFF\x10\x00\x00\x00WEBPVP8 " + b"\x02" * 100


@pytest.fixture(autouse=True)
def media(tmp_path, monkeypatch):
    folder = tmp_path / "product-images"
    monkeypatch.setattr(product_image_service, "media_dir", lambda: folder)
    return folder


def files(folder) -> list[str]:
    return sorted(p.name for p in folder.glob("*")) if folder.exists() else []


def image_path(url: str) -> str:
    assert url.startswith("/api/v1/product-images/")
    return url.removeprefix("/api/v1")


async def upload(client, h, pid, data, content_type="image/jpeg"):
    return await client.put(
        f"/products/{pid}/image", headers={**h, "Content-Type": content_type}, content=data
    )


async def test_unggah_ganti_dan_sajikan_foto(db, client, staff, media):
    lg = staff["LOGISTIK"]
    pid = await make_product(client, lg, await make_category(client, lg), "IMG-1")

    res = await upload(client, lg, pid, JPEG)
    assert res.status_code == 200, res.text
    first = res.json()["data"]["imageUrl"]
    assert first.endswith(".jpg") and files(media) == [first.rsplit("/", 1)[1]]

    # disajikan tanpa login, dengan tipe dari isi file dan cache permanen
    img = await client.get(image_path(first))
    assert img.status_code == 200 and img.content == JPEG
    assert img.headers["content-type"] == "image/jpeg"
    assert "immutable" in img.headers["cache-control"]
    again = await client.get(image_path(first), headers={"If-None-Match": img.headers["etag"]})
    assert again.status_code == 304

    # tipe ditentukan dari isi file, bukan header Content-Type yang dikirim
    res = await upload(client, lg, pid, PNG, content_type="image/jpeg")
    second = res.json()["data"]["imageUrl"]
    assert second != first
    assert (await client.get(image_path(second))).headers["content-type"] == "image/png"
    assert (await client.get(image_path(first))).status_code == 404  # foto lama dihapus
    assert files(media) == [second.rsplit("/", 1)[1]] and second.endswith(".png")

    # kasir juga menerima imageUrl (tanpa harga pokok)
    assert (await get_product(client, staff["KASIR"], pid))["imageUrl"] == second


async def test_validasi_dan_hak_akses(db, client, staff, media):
    lg = staff["LOGISTIK"]
    pid = await make_product(client, lg, await make_category(client, lg), "IMG-2")
    assert_error(await upload(client, staff["KASIR"], pid, PNG), 403, "FORBIDDEN")
    assert_error(await upload(client, staff["OWNER"], pid, PNG), 403, "FORBIDDEN")
    assert_error(await upload(client, lg, pid, b"bukan gambar", "image/png"), 415, "UNSUPPORTED_MEDIA_TYPE")
    assert_error(await upload(client, lg, pid, b""), 400, "BAD_REQUEST")
    assert_error(await upload(client, lg, pid, JPEG + b"\x00" * 1_500_000), 413, "PAYLOAD_TOO_LARGE")
    assert_error(await upload(client, lg, "6500000000000000000000aa", WEBP), 404, "NOT_FOUND")
    assert_error(await client.get("/product-images/bukan-id"), 404, "NOT_FOUND")
    for evil in ("..%2F..%2Fapp%2Fmain.py", "6500000000000000000000aa.exe", "6500000000000000000000aa.jpg"):
        assert (await client.get(f"/product-images/{evil}")).status_code == 404
    assert files(media) == []


async def test_url_luar_hapus_foto_dan_audit(db, client, staff, media):
    lg = staff["LOGISTIK"]
    cat = await make_category(client, lg)
    pid = await make_product(client, lg, cat, "IMG-3")
    internal = (await upload(client, lg, pid, WEBP)).json()["data"]["imageUrl"]
    body = {"sku": "IMG-3", "name": "Produk IMG-3", "categoryId": cat, "unit": "pcs", "sellingPrice": 4000}

    # imageUrl hanya boleh http(s) atau foto internal
    res = assert_error(
        await client.put(f"/products/{pid}", headers=lg, json={**body, "imageUrl": "javascript:alert(1)"}),
        422,
        "VALIDATION_ERROR",
    )
    assert res["error"]["details"][0]["field"] == "imageUrl"
    res = await client.put(f"/products/{pid}", headers=lg, json={**body, "imageUrl": internal})
    assert res.status_code == 200 and len(files(media)) == 1

    # diganti URL luar → foto internal tidak dibiarkan menumpuk
    res = await client.put(
        f"/products/{pid}", headers=lg, json={**body, "imageUrl": "https://contoh.id/a.jpg"}
    )
    assert res.json()["data"]["imageUrl"] == "https://contoh.id/a.jpg"
    assert files(media) == []

    await upload(client, lg, pid, PNG)
    res = await client.delete(f"/products/{pid}/image", headers=lg)
    assert res.status_code == 200 and res.json()["data"]["imageUrl"] is None
    assert files(media) == []
    descs = [a["description"] async for a in db.audit_logs.find({"module": "PRODUCT"}).sort("createdAt", 1)]
    assert "Mengganti foto produk IMG-3" in descs and descs[-1] == "Menghapus foto produk IMG-3"
