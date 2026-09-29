from typing import Literal

from pydantic import Field, field_validator

from app.core.enums import Role
from app.schemas.common import CamelModel, DocModel, UtcDatetime

StaffRole = Literal["OWNER", "LOGISTIK", "ADMIN", "KASIR"]  # MEMBER dicadangkan, belum bisa dibuat

USERNAME_PATTERN = r"^[a-z0-9._]{3,32}$"


def _normalize_username(v: str) -> str:
    return v.strip().lower() if isinstance(v, str) else v


class UserOut(DocModel):
    """Objek User (dokumen 04 §5). `passwordHash` tidak pernah ikut."""

    name: str
    username: str
    role: Role
    is_active: bool
    created_at: UtcDatetime
    updated_at: UtcDatetime


class UserBrief(DocModel):
    """User ringkas di response login."""

    name: str
    username: str
    role: Role


class UserCreate(CamelModel):
    name: str = Field(min_length=1, max_length=60)
    username: str = Field(
        pattern=USERNAME_PATTERN,
        description="3–32 karakter: huruf kecil, angka, titik, underscore. Otomatis di-lowercase.",
    )
    password: str = Field(min_length=8, max_length=72)  # bcrypt hanya memakai 72 byte pertama
    role: StaffRole

    _norm_username = field_validator("username", mode="before")(_normalize_username)

    @field_validator("name")
    @classmethod
    def _strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Nama wajib diisi")
        return v


class UserUpdate(CamelModel):
    name: str = Field(min_length=1, max_length=60)
    role: StaffRole

    @field_validator("name")
    @classmethod
    def _strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Nama wajib diisi")
        return v


class UserStatusUpdate(CamelModel):
    is_active: bool


class PasswordReset(CamelModel):
    new_password: str = Field(min_length=8, max_length=72)
