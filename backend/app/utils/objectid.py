from bson import ObjectId
from bson.errors import InvalidId

from app.core.errors import AppError


def parse_object_id(value: str, message: str = "Data tidak ditemukan") -> ObjectId:
    """ID dari URL/body → ObjectId. ID yang formatnya salah pasti tidak ada, jadi 404."""
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise AppError(404, "NOT_FOUND", message) from None


def optional_object_id(value: str | None, field: str) -> ObjectId | None:
    """Untuk filter query (?userId=...). Format salah → 422 agar frontend tahu filternya keliru."""
    if value is None or value == "":
        return None
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise AppError(
            422, "VALIDATION_ERROR", "Input tidak valid", [{"field": field, "message": "ID tidak valid"}]
        ) from None
