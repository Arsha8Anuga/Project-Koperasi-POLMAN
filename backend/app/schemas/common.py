"""Komponen schema yang dipakai bersama oleh modul BE-3.

Kalau BE-1 sudah membuat file dengan nama yang sama, gabungkan isinya.
"""

from __future__ import annotations

import math
import re
from datetime import datetime, timezone
from typing import Annotated, Any

from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict, PlainSerializer
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Basis semua schema. JSON memakai camelCase, kode Python memakai snake_case."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


def _format_utc(value: datetime) -> str:
    """Format ISO 8601 UTC, contoh 2026-09-28T03:42:10Z."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# Datetime yang keluar sebagai string UTC berakhiran Z.
UtcDatetime = Annotated[
    datetime,
    PlainSerializer(_format_utc, return_type=str, when_used="json"),
]

# Id dari database (ObjectId) otomatis diubah menjadi string hex.
IdStr = Annotated[str, BeforeValidator(lambda value: str(value))]

_HEX_24 = re.compile(r"^[0-9a-fA-F]{24}$")


def _check_object_id(value: str) -> str:
    if not _HEX_24.match(value):
        raise ValueError("ID tidak valid")
    return value


# Id pada request: harus berupa 24 karakter hex.
RequestId = Annotated[str, AfterValidator(_check_object_id)]


class PageMeta(CamelModel):
    page: int
    limit: int
    total: int
    total_pages: int


def ok_response(data: Any, message: str = "OK") -> dict:
    """Bungkus response sukses standar."""
    return {"success": True, "message": message, "data": data}


def paged_response(
    data: list[Any],
    page: int,
    limit: int,
    total: int,
    message: str = "OK",
    **extra: Any,
) -> dict:
    """Bungkus response sukses dengan pagination.

    Kunci tambahan (misalnya summary) diletakkan sejajar dengan meta.
    """
    meta = PageMeta(
        page=page,
        limit=limit,
        total=total,
        total_pages=math.ceil(total / limit) if limit else 0,
    )
    body = {
        "success": True,
        "message": message,
        "data": data,
        "meta": meta.model_dump(by_alias=True),
    }
    body.update(extra)
    return body
