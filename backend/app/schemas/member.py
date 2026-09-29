from datetime import date

from pydantic import Field, field_validator

from app.schemas.common import CamelModel, DocModel, ObjectIdStr, UtcDatetime

PHONE_PATTERN = r"^\+?[0-9]{8,15}$"


def _strip(v):
    return v.strip() if isinstance(v, str) else v


def _empty_to_none(v):
    v = _strip(v)
    return v or None


class MemberOut(DocModel):
    member_number: str
    name: str
    phone: str | None = None
    is_active: bool
    joined_at: date  # disimpan sebagai string "YYYY-MM-DD"
    created_at: UtcDatetime
    updated_at: UtcDatetime


class MemberLookup(CamelModel):
    """Response ringkas untuk kasir (dokumen 04 §7.4)."""

    id: ObjectIdStr
    member_number: str
    name: str


class MemberCreate(CamelModel):
    member_number: str = Field(min_length=1, max_length=20, description="Format bebas, disarankan KOP-NNN")
    name: str = Field(min_length=1, max_length=60)
    phone: str | None = Field(default=None, pattern=PHONE_PATTERN)
    joined_at: date | None = Field(default=None, description="Default: hari ini (WIB)")

    _s1 = field_validator("member_number", "name", mode="before")(_strip)
    _s2 = field_validator("phone", mode="before")(_empty_to_none)

    @field_validator("member_number")
    @classmethod
    def _upper(cls, v: str) -> str:
        return v.upper()


class MemberUpdate(CamelModel):
    name: str = Field(min_length=1, max_length=60)
    phone: str | None = Field(default=None, pattern=PHONE_PATTERN)
    is_active: bool

    _s1 = field_validator("name", mode="before")(_strip)
    _s2 = field_validator("phone", mode="before")(_empty_to_none)
