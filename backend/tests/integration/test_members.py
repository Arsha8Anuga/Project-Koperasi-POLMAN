from tests.conftest import assert_error, auth_header, make_user

MEMBER = {"name": "Budi Santoso", "phone": "08123456789", "joinedAt": "2026-01-10"}


async def test_crud_anggota(db, client, admin):
    _, headers = admin
    res = await client.post("/members", headers=headers, json=MEMBER)
    assert res.status_code == 201, res.text
    m = res.json()["data"]
    assert m["memberNumber"] == "KOP-001" and m["joinedAt"] == "2026-01-10" and m["isActive"] is True

    # nama sama boleh (orang berbeda), nomor tetap unik & berurutan
    res = await client.post("/members", headers=headers, json=MEMBER)
    assert res.json()["data"]["memberNumber"] == "KOP-002"

    res = await client.get(f"/members/{m['id']}", headers=headers)
    assert res.json()["data"]["name"] == "Budi Santoso"

    res = await client.put(
        f"/members/{m['id']}", headers=headers, json={"name": "Budi S.", "phone": "", "isActive": False}
    )
    assert res.status_code == 200, res.text
    data = res.json()["data"]
    assert data["name"] == "Budi S." and data["phone"] is None and data["isActive"] is False

    actions = sorted([lg["action"] async for lg in db.audit_logs.find({"module": "MEMBER"})])
    assert actions == ["CREATE", "CREATE", "DEACTIVATE", "UPDATE"]


async def test_joined_at_default_hari_ini_dan_validasi_telepon(db, client, admin):
    _, headers = admin
    res = await client.post("/members", headers=headers, json={"name": "Ani"})
    assert res.status_code == 201 and len(res.json()["data"]["joinedAt"]) == 10
    bad = {"name": "Ani", "phone": "abc"}
    assert_error(await client.post("/members", headers=headers, json=bad), 422, "VALIDATION_ERROR")


async def test_list_dan_search(db, client, admin):
    _, headers = admin
    for name in ["Budi", "Citra", "Dodi"]:
        await client.post("/members", headers=headers, json={"name": name})  # KOP-001..003
    res = await client.get("/members", headers=headers, params={"search": "dI"})
    assert sorted(m["name"] for m in res.json()["data"]) == ["Budi", "Dodi"]
    res = await client.get("/members", headers=headers, params={"search": "kop-003"})
    assert [m["name"] for m in res.json()["data"]] == ["Dodi"]


async def test_lookup_untuk_kasir(db, client, admin):
    _, admin_headers = admin
    res = await client.post("/members", headers=admin_headers, json=MEMBER)
    member_id = res.json()["data"]["id"]

    await make_user(db, "siti", "KASIR")
    await make_user(db, "rudi", "LOGISTIK")
    kasir = await auth_header(client, "siti", "KASIR")

    res = await client.get("/members/lookup/kop-001", headers=kasir)
    assert res.status_code == 200
    assert res.json()["data"] == {"id": member_id, "memberNumber": "KOP-001", "name": "Budi Santoso"}

    assert_error(await client.get("/members", headers=kasir), 403, "FORBIDDEN")
    assert_error(
        await client.get("/members/lookup/KOP-001", headers=await auth_header(client, "rudi")),
        403,
        "FORBIDDEN",
    )
    assert_error(await client.get("/members/lookup/KOP-999", headers=kasir), 404, "NOT_FOUND")

    await client.put(
        f"/members/{member_id}", headers=admin_headers, json={"name": "Budi Santoso", "isActive": False}
    )
    assert_error(await client.get("/members/lookup/KOP-001", headers=kasir), 404, "NOT_FOUND")


async def test_kasir_boleh_daftar_tapi_tidak_boleh_ubah(db, client, admin):
    _, admin_headers = admin
    await make_user(db, "siti", "KASIR")
    await make_user(db, "rudi", "LOGISTIK")
    kasir = await auth_header(client, "siti", "KASIR")

    # nomor dari client diabaikan
    body = {"memberNumber": "HACK-1", "name": "Wati", "phone": "0812345678"}
    res = await client.post("/members", headers=kasir, json=body)
    assert res.status_code == 201, res.text
    m = res.json()["data"]
    assert m["memberNumber"] == "KOP-001"

    # langsung bisa dipakai di kasir
    res = await client.get("/members/lookup/kop-001", headers=kasir)
    assert res.json()["data"]["name"] == "Wati"

    upd = {"name": "Wati X", "phone": None, "isActive": False}
    assert_error(await client.put(f"/members/{m['id']}", headers=kasir, json=upd), 403, "FORBIDDEN")
    assert_error(await client.get(f"/members/{m['id']}", headers=kasir), 403, "FORBIDDEN")

    logistik = await auth_header(client, "rudi", "ADMIN")
    assert_error(await client.post("/members", headers=logistik, json={"name": "X"}), 403, "FORBIDDEN")

    log = await db.audit_logs.find_one({"module": "MEMBER", "action": "CREATE"})
    assert log["user"]["role"] == "KASIR" and "KOP-001" in log["description"]


async def test_nomor_melanjutkan_data_lama(db, client, admin):
    """Data seed/impor diinsert langsung tanpa counter: nomor baru harus melanjutkan yang terbesar."""
    _, headers = admin

    async def insert_raw(number: str) -> None:
        doc = {"memberNumber": number, "name": number, "isActive": True, "joinedAt": "2026-01-01"}
        await db.members.insert_one(doc)

    for n in ("KOP-001", "KOP-007", "KOP-010", "LAMA-99"):
        await insert_raw(n)
    res = await client.post("/members", headers=headers, json={"name": "Baru"})
    assert res.json()["data"]["memberNumber"] == "KOP-011"

    # counter tertinggal (mis. data diinsert lagi setelah counter dibuat) → tetap tidak bentrok
    await insert_raw("KOP-012")
    await insert_raw("KOP-013")
    res = await client.post("/members", headers=headers, json={"name": "Baru 2"})
    assert res.status_code == 201 and res.json()["data"]["memberNumber"] == "KOP-014"
