from tests.conftest import assert_error, auth_header, login, make_user


async def test_login_kasir_sukses_dan_format_response(db, client):
    await make_user(db, "siti", "KASIR", name="Siti Kasir")
    res = await login(client, "siti", "KASIR")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["success"] is True and body["message"] == "Login berhasil"
    data = body["data"]
    assert set(data) == {"token", "expiresAt", "user"}
    assert data["expiresAt"].endswith("Z")
    assert data["user"]["username"] == "siti" and data["user"]["role"] == "KASIR"
    assert "passwordHash" not in data["user"] and "_id" not in data["user"]
    assert len(data["user"]["id"]) == 24


async def test_login_username_tidak_case_sensitive(db, client):
    await make_user(db, "siti", "KASIR")
    assert (await login(client, "  SiTi ", "KASIR")).status_code == 200


async def test_password_salah_dan_user_tidak_ada_sama_sama_401(db, client):
    await make_user(db, "siti", "KASIR")
    assert_error(await login(client, "siti", "KASIR", "salah-banget"), 401, "INVALID_CREDENTIALS")
    assert_error(await login(client, "hantu", "KASIR"), 401, "INVALID_CREDENTIALS")


async def test_login_ke_aplikasi_yang_salah_403(db, client):
    await make_user(db, "siti", "KASIR")
    await make_user(db, "owner", "OWNER")
    assert_error(await login(client, "siti", "ADMIN"), 403, "FORBIDDEN")
    assert_error(await login(client, "owner", "KASIR"), 403, "FORBIDDEN")


async def test_login_user_nonaktif_403(db, client):
    await make_user(db, "siti", "KASIR", active=False)
    assert_error(await login(client, "siti", "KASIR"), 403, "ACCOUNT_INACTIVE")


async def test_login_body_tidak_valid_422_format_standar(db, client):
    res = await client.post("/auth/login", json={"username": "x", "app": "POS"})
    body = assert_error(res, 422, "VALIDATION_ERROR")
    fields = {d["field"]: d["message"] for d in body["error"]["details"]}
    assert fields["password"] == "Wajib diisi"
    assert "app" in fields
    assert "detail" not in body  # format bawaan FastAPI tidak boleh bocor


async def test_me_tanpa_token_dan_token_rusak_401(db, client):
    assert_error(await client.get("/auth/me"), 401, "UNAUTHORIZED")
    assert_error(
        await client.get("/auth/me", headers={"Authorization": "Bearer abc.def.ghi"}), 401, "UNAUTHORIZED"
    )


async def test_me_mengembalikan_objek_user(db, client):
    await make_user(db, "owner", "OWNER", name="Oscar")
    res = await client.get("/auth/me", headers=await auth_header(client, "owner"))
    assert res.status_code == 200
    user = res.json()["data"]
    assert set(user) == {"id", "name", "username", "role", "isActive", "createdAt", "updatedAt"}
    assert user["createdAt"].endswith("Z")


async def test_user_dinonaktifkan_langsung_terkunci_walau_token_masih_berlaku(db, client):
    user = await make_user(db, "siti", "KASIR")
    headers = await auth_header(client, "siti", "KASIR")
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"isActive": False}})
    assert_error(await client.get("/auth/me", headers=headers), 403, "ACCOUNT_INACTIVE")


async def test_login_dan_logout_tercatat_di_audit(db, client):
    await make_user(db, "siti", "KASIR")
    headers = await auth_header(client, "siti", "KASIR")
    assert (await client.post("/auth/logout", headers=headers)).status_code == 200
    logs = await db.audit_logs.find({}, sort=[("createdAt", 1), ("_id", 1)]).to_list()
    assert [lg["action"] for lg in logs] == ["LOGIN", "LOGOUT"]
    assert logs[0]["module"] == "AUTH" and logs[0]["ip"] == "10.0.0.7"
    assert logs[0]["user"]["role"] == "KASIR"


async def test_ganti_password(db, client):
    await make_user(db, "siti", "KASIR")
    headers = await auth_header(client, "siti", "KASIR")

    res = await client.put(
        "/auth/password", headers=headers, json={"oldPassword": "keliru123", "newPassword": "barulagi456"}
    )
    assert_error(res, 400, "BAD_REQUEST")  # BUKAN 401, supaya frontend tidak logout

    res = await client.put(
        "/auth/password", headers=headers, json={"oldPassword": "password123", "newPassword": "pendek"}
    )
    assert_error(res, 422, "VALIDATION_ERROR")

    res = await client.put(
        "/auth/password", headers=headers, json={"oldPassword": "password123", "newPassword": "barulagi456"}
    )
    assert res.status_code == 200, res.text
    assert_error(await login(client, "siti", "KASIR"), 401, "INVALID_CREDENTIALS")
    assert (await login(client, "siti", "KASIR", "barulagi456")).status_code == 200


async def test_endpoint_tidak_ada_404_format_standar(db, client):
    assert_error(await client.get("/tidak-ada"), 404, "NOT_FOUND")
