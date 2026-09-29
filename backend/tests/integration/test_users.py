from tests.conftest import assert_error, auth_header, make_user

NEW_USER = {"name": "Budi Kasir", "username": "budi", "password": "rahasia123", "role": "KASIR"}


async def test_rbac_hanya_admin(db, client):
    for username, role, app in [
        ("kasir", "KASIR", "KASIR"),
        ("owner", "OWNER", "ADMIN"),
        ("logistik", "LOGISTIK", "ADMIN"),
    ]:
        await make_user(db, username, role)
        headers = await auth_header(client, username, app)
        assert_error(await client.get("/users", headers=headers), 403, "FORBIDDEN")
        assert_error(await client.post("/users", headers=headers, json=NEW_USER), 403, "FORBIDDEN")


async def test_buat_user_dan_duplikat(db, client, admin):
    _, headers = admin
    res = await client.post("/users", headers=headers, json={**NEW_USER, "username": "Budi"})
    assert res.status_code == 201, res.text
    user = res.json()["data"]
    assert user["username"] == "budi" and user["isActive"] is True
    assert "passwordHash" not in user and "password" not in user

    assert_error(await client.post("/users", headers=headers, json=NEW_USER), 409, "DUPLICATE")

    log = await db.audit_logs.find_one({"action": "CREATE", "module": "USER"})
    assert log and "budi" in log["description"]


async def test_buat_user_validasi(db, client, admin):
    _, headers = admin
    bad = {"name": "", "username": "a b", "password": "123", "role": "MEMBER"}
    body = assert_error(await client.post("/users", headers=headers, json=bad), 422, "VALIDATION_ERROR")
    assert {d["field"] for d in body["error"]["details"]} == {"name", "username", "password", "role"}


async def test_list_pagination_filter_search(db, client, admin):
    _, headers = admin
    for i in range(5):
        await make_user(db, f"kasir{i}", "KASIR", active=i != 0)
    await make_user(db, "rudi", "LOGISTIK", name="Rudi Gudang")

    res = await client.get("/users", headers=headers, params={"limit": 2, "page": 2})
    body = res.json()
    assert body["meta"] == {"page": 2, "limit": 2, "total": 7, "totalPages": 4}
    assert len(body["data"]) == 2

    res = await client.get("/users", headers=headers, params={"role": "KASIR", "isActive": "true"})
    assert res.json()["meta"]["total"] == 4

    res = await client.get("/users", headers=headers, params={"search": "gUDa"})
    assert [u["username"] for u in res.json()["data"]] == ["rudi"]

    res = await client.get("/users", headers=headers, params={"search": ".*"})  # bukan regex
    assert res.json()["meta"]["total"] == 0

    assert_error(await client.get("/users", headers=headers, params={"limit": 101}), 422, "VALIDATION_ERROR")


async def test_get_update_404(db, client, admin):
    _, headers = admin
    assert_error(await client.get("/users/bukan-id", headers=headers), 404, "NOT_FOUND")
    assert_error(await client.get("/users/66f7a1b2c3d4e5f607182930", headers=headers), 404, "NOT_FOUND")


async def test_update_user_dan_audit(db, client, admin):
    _, headers = admin
    target = await make_user(db, "budi", "KASIR", name="Budi")
    res = await client.put(
        f"/users/{target['_id']}",
        headers=headers,
        json={"name": "Budi Santoso", "role": "LOGISTIK", "username": "hacker"},
    )
    assert res.status_code == 200, res.text
    data = res.json()["data"]
    assert data["name"] == "Budi Santoso" and data["role"] == "LOGISTIK" and data["username"] == "budi"
    log = await db.audit_logs.find_one({"action": "UPDATE", "module": "USER"})
    assert "KASIR menjadi LOGISTIK" in log["description"]


async def test_admin_tidak_bisa_nonaktifkan_atau_ubah_role_diri_sendiri(db, client, admin):
    me, headers = admin
    assert_error(
        await client.patch(f"/users/{me['_id']}/status", headers=headers, json={"isActive": False}),
        400,
        "BAD_REQUEST",
    )
    assert_error(
        await client.put(f"/users/{me['_id']}", headers=headers, json={"name": "X", "role": "KASIR"}),
        400,
        "BAD_REQUEST",
    )


async def test_nonaktifkan_lalu_aktifkan_user(db, client, admin):
    _, headers = admin
    target = await make_user(db, "budi", "KASIR")
    res = await client.patch(f"/users/{target['_id']}/status", headers=headers, json={"isActive": False})
    assert res.status_code == 200 and res.json()["data"]["isActive"] is False
    res = await client.patch(f"/users/{target['_id']}/status", headers=headers, json={"isActive": True})
    assert res.json()["data"]["isActive"] is True
    actions = [lg["action"] async for lg in db.audit_logs.find({"module": "USER"}).sort("createdAt", 1)]
    assert actions == ["DEACTIVATE", "ACTIVATE"]


async def test_reset_password(db, client, admin):
    _, headers = admin
    target = await make_user(db, "budi", "KASIR")
    res = await client.post(
        f"/users/{target['_id']}/reset-password", headers=headers, json={"newPassword": "passwordbaru1"}
    )
    assert res.status_code == 200, res.text
    res = await client.post(
        "/auth/login", json={"username": "budi", "password": "passwordbaru1", "app": "KASIR"}
    )
    assert res.status_code == 200
    assert await db.audit_logs.count_documents({"action": "RESET_PASSWORD"}) == 1


async def test_perubahan_role_langsung_berlaku_tanpa_login_ulang(db, client):
    user = await make_user(db, "admin", "ADMIN")
    headers = await auth_header(client, "admin")
    assert (await client.get("/users", headers=headers)).status_code == 200
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"role": "LOGISTIK"}})
    assert_error(await client.get("/users", headers=headers), 403, "FORBIDDEN")
