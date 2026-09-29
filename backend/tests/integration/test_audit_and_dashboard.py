from datetime import timedelta

from app.utils.time import utcnow
from tests.conftest import assert_error, auth_header, make_user


async def test_audit_logs_filter_dan_urutan(db, client, admin):
    admin_user, headers = admin
    await client.post("/members", headers=headers, json={"memberNumber": "KOP-001", "name": "Budi"})
    await make_user(db, "siti", "KASIR")
    await auth_header(client, "siti", "KASIR")  # LOGIN oleh siti

    res = await client.get("/audit-logs", headers=headers)
    body = res.json()
    assert res.status_code == 200 and body["meta"]["total"] == 3  # login admin, create member, login siti
    first = body["data"][0]
    assert set(first) == {"id", "user", "action", "module", "referenceId", "description", "ip", "createdAt"}
    assert first["user"]["id"] and first["createdAt"].endswith("Z")

    res = await client.get("/audit-logs", headers=headers, params={"module": "MEMBER"})
    assert [lg["action"] for lg in res.json()["data"]] == ["CREATE"]

    res = await client.get(
        "/audit-logs", headers=headers, params={"userId": str(admin_user["_id"]), "action": "LOGIN"}
    )
    assert res.json()["meta"]["total"] == 1

    assert_error(
        await client.get("/audit-logs", headers=headers, params={"userId": "zzz"}), 422, "VALIDATION_ERROR"
    )
    assert_error(
        await client.get("/audit-logs", headers=headers, params={"module": "NGAWUR"}), 422, "VALIDATION_ERROR"
    )


async def test_audit_logs_filter_tanggal_wib(db, client, admin):
    admin_user, headers = admin
    # 2026-09-27 23:30 WIB = 2026-09-27 16:30 UTC  → masuk tanggal 27
    # 2026-09-28 00:30 WIB = 2026-09-27 17:30 UTC  → masuk tanggal 28 walau UTC-nya tanggal 27
    from datetime import UTC, datetime

    base = {
        "user": {"id": admin_user["_id"], "name": "A", "role": "ADMIN"},
        "action": "UPDATE",
        "module": "PRODUCT",
        "referenceId": None,
        "description": "x",
        "ip": None,
    }
    await db.audit_logs.insert_many(
        [
            {**base, "description": "27", "createdAt": datetime(2026, 9, 27, 16, 30, tzinfo=UTC)},
            {**base, "description": "28", "createdAt": datetime(2026, 9, 27, 17, 30, tzinfo=UTC)},
        ]
    )
    res = await client.get(
        "/audit-logs", headers=headers, params={"from": "2026-09-28", "to": "2026-09-28", "module": "PRODUCT"}
    )
    assert [lg["description"] for lg in res.json()["data"]] == ["28"]
    res = await client.get(
        "/audit-logs", headers=headers, params={"from": "2026-09-27", "to": "2026-09-27", "module": "PRODUCT"}
    )
    assert [lg["description"] for lg in res.json()["data"]] == ["27"]


async def test_audit_logs_hanya_admin(db, client):
    await make_user(db, "owner", "OWNER")
    assert_error(
        await client.get("/audit-logs", headers=await auth_header(client, "owner")), 403, "FORBIDDEN"
    )


async def test_dashboard_admin(db, client, admin):
    _, headers = admin
    await make_user(db, "k1", "KASIR")
    await make_user(db, "k2", "KASIR")
    await make_user(db, "k3", "KASIR", active=False)
    await client.post("/members", headers=headers, json={"memberNumber": "KOP-001", "name": "Budi"})
    await db.audit_logs.insert_one(
        {
            "user": {"id": None, "name": "x", "role": "ADMIN"},
            "action": "LOGIN",
            "module": "AUTH",
            "description": "lama",
            "createdAt": utcnow() - timedelta(days=3),
        }
    )

    res = await client.get("/dashboard/summary", headers=headers)
    assert res.status_code == 200, res.text
    assert res.json()["data"] == {
        "activeUsers": 3,
        "usersByRole": {"OWNER": 0, "LOGISTIK": 0, "ADMIN": 1, "KASIR": 2},
        "activeMembers": 1,
        "auditLogsToday": 2,  # login admin + create member
    }


async def test_dashboard_per_role(db, client):
    await make_user(db, "rudi", "LOGISTIK")
    await make_user(db, "owner", "OWNER")
    await make_user(db, "siti", "KASIR")
    res = await client.get("/dashboard/summary", headers=await auth_header(client, "rudi"))
    assert set(res.json()["data"]) == {
        "activeProducts",
        "lowStockCount",
        "outOfStockCount",
        "restocksThisMonth",
    }
    res = await client.get("/dashboard/summary", headers=await auth_header(client, "owner"))
    assert set(res.json()["data"]) == {"salesToday", "transactionsToday", "grossProfitToday", "restockToday"}
    res = await client.get("/dashboard/summary", headers=await auth_header(client, "siti", "KASIR"))
    assert_error(res, 403, "FORBIDDEN")
