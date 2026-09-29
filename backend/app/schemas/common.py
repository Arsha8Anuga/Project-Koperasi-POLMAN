"""Model dasar & wrapper response bersama (milik integrator). Schema domain ada di file masing-masing.

- `CamelModel`: field Python snake_case, JSON camelCase (dokumen 04 §1).
- `ObjectIdStr` / `IdStr`: menerima ObjectId dari MongoDB, keluar sebagai string hex.
- `RequestId`: ID di body request, wajib 24 karakter hex (422 kalau tidak).
- `DocModel`: untuk objek yang dibaca dari MongoDB — `_id` otomatis menjadi `id`.
- `ApiResponse[T]` / `PaginatedResponse[T]`: bentuk response dokumen 04 §2, dipakai sebagai
  `response_model` supaya /docs menampilkan bentuk JSON yang benar ke tim frontend.
"""

import re
from datetime import UTC, datetime
from typing import Annotated, Any, Generic, TypeVar

from bson import ObjectId
from pydantic import (
    AfterValidator,
    AliasChoices,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PlainSerializer,
)
from pydantic.alias_generators import to_camel

_HEX_24 = re.compile(r"^[0-9a-fA-F]{24}$")


def _oid_to_str(v: Any) -> Any:
    return str(v) if isinstance(v, ObjectId) else v


def _as_utc(v: Any) -> Any:
    # Data lama/naive dianggap UTC.
    if isinstance(v, datetime) and v.tzinfo is None:
        return v.replace(tzinfo=UTC)
    return v


ObjectIdStr = Annotated[str, BeforeValidator(_oid_to_str)]
IdStr = ObjectIdStr  # nama lain yang dipakai modul transaksi


def _check_object_id(value: str) -> str:
    if not isinstance(value, str) or not _HEX_24.match(value):
        raise ValueError("ID tidak valid")
    return value.lower()


# ID pada REQUEST body: wajib 24 karakter hex, jadi ID ngawur langsung 422 di validasi.
RequestId = Annotated[str, AfterValidator(_check_object_id)]

# Selalu dikirim sebagai "2026-09-28T03:42:10Z" (dokumen 04 §1).
UtcDatetime = Annotated[
    datetime,
    BeforeValidator(_as_utc),
    PlainSerializer(lambda d: d.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), return_type=str),
]


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class DocModel(CamelModel):
    id: ObjectIdStr = Field(validation_alias=AliasChoices("_id", "id"))


class PageMeta(CamelModel):
    page: int
    limit: int
    total: int
    total_pages: int


T = TypeVar("T")


class ApiResponse(CamelModel, Generic[T]):
    success: bool = True
    message: str = "OK"
    data: T


class PaginatedResponse(CamelModel, Generic[T]):
    """Butuh field tambahan sejajar `meta` (mis. `summary` di /transactions)? Buat subclass:

        class TransactionPage(PaginatedResponse[TransactionOut]):
            summary: TransactionSummary

    Tanpa subclass, field tambahan dari `paginated(..., summary=...)` akan DIBUANG oleh FastAPI.
    """

    success: bool = True
    message: str = "OK"
    data: list[T]
    meta: PageMeta


class ErrorInfo(CamelModel):
    code: str
    details: list[dict[str, Any]] = []


class ErrorResponse(CamelModel):
    success: bool = False
    message: str
    error: ErrorInfo


# Dipakai di `responses=` router supaya /docs juga menampilkan bentuk error.
ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    code: {"model": ErrorResponse} for code in (400, 401, 403, 404, 409, 422)
}
