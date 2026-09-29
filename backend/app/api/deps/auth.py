from collections.abc import Awaitable, Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pymongo.asynchronous.database import AsyncDatabase

from app.api.deps.database import get_db
from app.core.enums import Role
from app.core.errors import AppError
from app.core.security import TokenError, decode_access_token
from app.repositories import user_repo
from app.schemas.auth import CurrentUser

# auto_error=False supaya token kosong juga lewat format error kita (401 UNAUTHORIZED),
# bukan format bawaan FastAPI.
_bearer = HTTPBearer(auto_error=False, description="Token dari POST /auth/login")


def _unauthorized(message: str = "Sesi tidak valid, silakan login ulang") -> AppError:
    return AppError(401, "UNAUTHORIZED", message)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncDatabase = Depends(get_db),
) -> CurrentUser:
    if credentials is None or not credentials.credentials:
        raise _unauthorized("Silakan login terlebih dahulu")
    try:
        payload = decode_access_token(credentials.credentials)
    except TokenError:
        raise _unauthorized() from None

    user = await user_repo.find_by_id_str(db, payload["sub"])
    if user is None:
        raise _unauthorized()
    if not user.get("isActive", False):
        raise AppError(403, "ACCOUNT_INACTIVE", "Akun Anda telah dinonaktifkan")

    # Role dari DB, bukan dari token: perubahan role oleh admin langsung berlaku.
    return CurrentUser(id=str(user["_id"]), name=user["name"], username=user["username"], role=user["role"])


def require_roles(*allowed: Role) -> Callable[..., Awaitable[CurrentUser]]:
    """Pemakaian: `user: CurrentUser = Depends(require_roles(Role.LOGISTIK, Role.OWNER))`."""
    allowed_set = frozenset(allowed)

    async def checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in allowed_set:
            raise AppError(403, "FORBIDDEN", "Anda tidak memiliki akses ke fitur ini")
        return user

    return checker
