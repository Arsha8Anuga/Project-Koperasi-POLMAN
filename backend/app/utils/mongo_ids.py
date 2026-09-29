"""Fungsi bantu untuk ObjectId."""

from __future__ import annotations

import re
from typing import Any

from bson import ObjectId

_HEX_24 = re.compile(r"^[0-9a-fA-F]{24}$")


def parse_object_id(value: Any) -> ObjectId | None:
    """Ubah nilai menjadi ObjectId. Mengembalikan None jika bentuknya tidak valid."""
    if isinstance(value, ObjectId):
        return value
    if isinstance(value, str) and _HEX_24.match(value):
        return ObjectId(value)
    return None


def id_variants(value: ObjectId | str) -> list[ObjectId | str]:
    """Kembalikan ObjectId dan bentuk string-nya.

    Dipakai pada filter untuk id di dalam dokumen snapshot (cashier.id, items.productId, dan
    sebagainya). Dengan cara ini query tetap cocok, apa pun bentuk id yang disimpan modul lain.
    """
    oid = parse_object_id(value)
    if oid is None:
        return [value]
    return [oid, str(oid)]
