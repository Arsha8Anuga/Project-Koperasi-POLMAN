"""Konversi ID. Tiga fungsi, tiga perilaku saat ID-nya ngawur:

- `parse_object_id(v)`     → 404 NOT_FOUND   (ID di URL: /products/{id})
- `optional_object_id(v)`  → 422 VALIDATION  (ID di query filter: ?supplierId=...)
- `try_object_id(v)`       → None            (pengecekan manual di service)
"""

import re
from typing import Any

from bson import ObjectId

from app.core.errors import AppError

_HEX_24 = re.compile(r"^[0-9a-fA-F]{24}$")


def try_object_id(value: Any) -> ObjectId | None:
    if isinstance(value, ObjectId):
        return value
    if isinstance(value, str) and _HEX_24.match(value):
        return ObjectId(value)
    return None


def parse_object_id(value: Any, message: str = "Data tidak ditemukan") -> ObjectId:
    """ID dari URL → ObjectId. ID yang formatnya salah pasti tidak ada, jadi 404."""
    oid = try_object_id(value)
    if oid is None:
        raise AppError(404, "NOT_FOUND", message)
    return oid


def optional_object_id(value: str | None, field: str) -> ObjectId | None:
    """Untuk filter query. Kosong → None; format salah → 422 agar frontend tahu filternya keliru."""
    if value is None or value == "":
        return None
    oid = try_object_id(value)
    if oid is None:
        raise AppError(
            422, "VALIDATION_ERROR", "Input tidak valid", [{"field": field, "message": "ID tidak valid"}]
        )
    return oid
