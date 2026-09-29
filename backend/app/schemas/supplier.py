from datetime import datetime
from pydantic import Field
from app.schemas.category import CamelModel   # ganti kalau CamelModel ada di file lain / punya BE-1


class SupplierCreate(CamelModel):
    supplier_code: str = Field(min_length=1, max_length=30)
    name: str = Field(min_length=1, max_length=120)
    contact_person: str | None = None
    phone: str | None = None
    email: str | None = None          # sengaja str biasa, EmailStr butuh library tambahan
    address: str | None = None
    notes: str | None = None


SupplierUpdate = SupplierCreate       # body PUT sama dengan POST


class SupplierStatus(CamelModel):
    is_active: bool


class SupplierOut(CamelModel):
    id: str
    supplier_code: str
    name: str
    contact_person: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    notes: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime