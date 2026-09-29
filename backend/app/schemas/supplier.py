from pydantic import Field, field_validator

from app.schemas.common import CamelModel, DocModel, UtcDatetime

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
PHONE_PATTERN = r"^\+?[0-9]{8,15}$"


def _clean(v):
    if isinstance(v, str):
        v = v.strip()
        return v or None
    return v


class SupplierOut(DocModel):
    supplier_code: str
    name: str
    contact_person: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    notes: str | None = None
    is_active: bool
    created_at: UtcDatetime
    updated_at: UtcDatetime


class SupplierCreate(CamelModel):
    supplier_code: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=120)
    contact_person: str | None = Field(default=None, max_length=60)
    phone: str | None = Field(default=None, pattern=PHONE_PATTERN)
    email: str | None = Field(default=None, pattern=EMAIL_PATTERN, max_length=120)
    address: str | None = Field(default=None, max_length=300)
    notes: str | None = Field(default=None, max_length=300)

    _c = field_validator(
        "supplier_code", "name", "contact_person", "phone", "email", "address", "notes", mode="before"
    )(_clean)

    @field_validator("supplier_code")
    @classmethod
    def _upper(cls, v: str) -> str:
        return v.upper()


SupplierUpdate = SupplierCreate


class SupplierStatusUpdate(CamelModel):
    is_active: bool
