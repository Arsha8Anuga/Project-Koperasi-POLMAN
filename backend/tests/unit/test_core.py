import os
from datetime import UTC, date, datetime

os.environ.setdefault("JWT_SECRET", "test-secret-" + "x" * 40)

import pytest  # noqa: E402

from app.core.security import (  # noqa: E402
    TokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.middlewares.error_handler import _field_path, _translate  # noqa: E402
from app.utils.time import wib_range_to_utc  # noqa: E402


def test_hash_dan_verify_password():
    h = hash_password("rahasia123")
    assert h != "rahasia123"
    assert verify_password("rahasia123", h)
    assert not verify_password("salah", h)
    assert not verify_password("rahasia123", "bukan-hash-bcrypt")


def test_jwt_bolak_balik_dan_token_rusak():
    token, exp = create_access_token("66f7a1b2c3d4e5f607182930", "KASIR", "Siti")
    payload = decode_access_token(token)
    assert payload["sub"] == "66f7a1b2c3d4e5f607182930" and payload["role"] == "KASIR"
    assert exp.tzinfo is not None
    with pytest.raises(TokenError):
        decode_access_token(token + "x")


def test_rentang_tanggal_wib_ke_utc():
    start, end = wib_range_to_utc(date(2026, 9, 28), date(2026, 9, 28))
    assert start == datetime(2026, 9, 27, 17, 0, tzinfo=UTC)
    assert end == datetime(2026, 9, 28, 17, 0, tzinfo=UTC)
    assert wib_range_to_utc(None, None) == (None, None)


def test_path_field_error():
    assert _field_path(("body", "items", 1, "quantity")) == "items[1].quantity"
    assert _field_path(("query", "limit")) == "limit"
    assert _field_path(("body",)) == "body"


def test_terjemahan_pesan_validasi():
    assert _translate({"type": "missing"}) == "Wajib diisi"
    assert _translate({"type": "string_too_short", "ctx": {"min_length": 8}}) == "Minimal 8 karakter"
    assert _translate({"type": "less_than_equal", "ctx": {"le": 100}}) == "Maksimal 100"
