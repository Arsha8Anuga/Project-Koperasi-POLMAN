from tests.conftest import assert_error, auth_header, make_user

MEMBER = {"memberNumber": "kop-001", "name": "Budi Santoso", "phone": "08123456789", "joinedAt": "2026-01-10"}


async def test_crud_anggota(db, client, admin):
    _, headers = admin
    res = await client.post("/members", headers=headers, json=MEMBER)
    assert res.status_code == 201, res.text
    m = res.json()["data"]
    assert m["memberNumber"] == "KOP-001" and m["joinedAt"] == "2026-01-10" and m["isActive"] is True

    assert_error(await client.post("/members", headers=headers, json=MEMBER), 409, "DUPLICATE")

    res = await client.get(f"/members/{m['id']}", headers=headers)
    assert res.json()["data"]["name"] == "Budi Santoso"

    res = await client.put(
        f"/members/{m['id']}", headers=headers, json={"name": "Budi S.", "phone": "", "isActive": False}
    )
    assert res.status_code == 200, res.text
    data = res.json()["data"]
    assert data["name"] == "Budi S." and data["phone"] is None and data["isActive"] is False

    actions = sorted([lg["action"] async for lg in db.audit_logs.find({"module": "MEMBER"})])
    assert actions == ["CREATE", "DEACTIVATE", "UPDATE"]


async def test_joined_at_default_hari_ini_dan_validasi_telepon(db, client, admin):
    _, headers = admin
    res = await client.post("/members", headers=headers, json={"memberNumber": "KOP-002", "name": "Ani"})
    assert res.status_code == 201 and len(res.json()["data"]["joinedAt"]) == 10
    bad = {"memberNumber": "KOP-003", "name": "Ani", "phone": "abc"}
    assert_error(await client.post("/members", headers=headers, json=bad), 422, "VALIDATION_ERROR")


async def test_list_dan_search(db, client, admin):
    _, headers = admin
    for i, name in enumerate(["Budi", "Citra", "Dodi"], 1):
        await client.post("/members", headers=headers, json={"memberNumber": f"KOP-00{i}", "name": name})
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
