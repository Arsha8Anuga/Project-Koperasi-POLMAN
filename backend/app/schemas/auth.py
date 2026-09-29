from pydantic import Field, field_validator

from app.core.enums import App, Role
from app.schemas.common import CamelModel, UtcDatetime
from app.schemas.user import UserBrief


class CurrentUser(CamelModel):
    """User yang sedang login, hasil `get_current_user`. Role & status dibaca dari DATABASE,
    bukan dari JWT, jadi perubahan role oleh admin langsung berlaku."""

    id: str
    name: str
    username: str
    role: Role


class LoginRequest(CamelModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)
    app: App

    @field_validator("username", mode="before")
    @classmethod
    def _norm(cls, v: str) -> str:
        return v.strip().lower() if isinstance(v, str) else v


class LoginData(CamelModel):
    token: str
    expires_at: UtcDatetime
    user: UserBrief


class PasswordChange(CamelModel):
    old_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=72)
