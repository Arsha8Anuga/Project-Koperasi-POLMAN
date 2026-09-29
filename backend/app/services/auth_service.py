from pymongo.asynchronous.database import AsyncDatabase

from app.core.enums import APP_ROLES, AuditAction, AuditModule
from app.core.errors import AppError
from app.core.security import (
    ahash_password,
    averify_dummy,
    averify_password,
    create_access_token,
)
from app.repositories import user_repo
from app.schemas.auth import CurrentUser, LoginData, LoginRequest, PasswordChange
from app.schemas.user import UserBrief, UserOut
from app.services import audit_service as audit
from app.utils.objectid import parse_object_id
from app.utils.time import utcnow


def _invalid() -> AppError:
    return AppError(401, "INVALID_CREDENTIALS", "Username atau password salah")


def _actor(user: dict) -> CurrentUser:
    return CurrentUser(id=str(user["_id"]), name=user["name"], username=user["username"], role=user["role"])


async def login(db: AsyncDatabase, body: LoginRequest) -> LoginData:
    user = await user_repo.find_by_username(db, body.username)
    if user is None:
        await averify_dummy(body.password)  # samakan waktu respons
        raise _invalid()
    if not await averify_password(body.password, user["passwordHash"]):
        raise _invalid()

    # Status & aplikasi dicek SETELAH password benar, supaya orang yang tidak tahu
    # password tidak bisa mengetahui status/role sebuah akun.
    if not user.get("isActive", False):
        raise AppError(403, "ACCOUNT_INACTIVE", "Akun Anda telah dinonaktifkan")
    if user["role"] not in APP_ROLES[body.app]:
        app_name = "kasir" if body.app == "KASIR" else "admin"
        raise AppError(403, "FORBIDDEN", f"Akun Anda tidak dapat login ke aplikasi {app_name}")

    token, expires_at = create_access_token(str(user["_id"]), user["role"], user["name"])
    await audit.log(
        db, _actor(user), AuditAction.LOGIN, AuditModule.AUTH, user["_id"], f"Login ke aplikasi {body.app}"
    )
    return LoginData(token=token, expires_at=expires_at, user=UserBrief.model_validate(user))


async def me(db: AsyncDatabase, current: CurrentUser) -> UserOut:
    user = await user_repo.find_by_id(db, parse_object_id(current.id))
    if user is None:
        raise AppError(401, "UNAUTHORIZED", "Sesi tidak valid, silakan login ulang")
    return UserOut.model_validate(user)


async def logout(db: AsyncDatabase, current: CurrentUser) -> None:
    await audit.log(db, current, AuditAction.LOGOUT, AuditModule.AUTH, current.id, "Logout")


async def change_password(db: AsyncDatabase, current: CurrentUser, body: PasswordChange) -> None:
    user_id = parse_object_id(current.id)
    user = await user_repo.find_by_id(db, user_id)
    if user is None:
        raise AppError(401, "UNAUTHORIZED", "Sesi tidak valid, silakan login ulang")
    # Sengaja 400, BUKAN 401: interceptor frontend me-logout user pada setiap 401.
    if not await averify_password(body.old_password, user["passwordHash"]):
        raise AppError(
            400,
            "BAD_REQUEST",
            "Password lama salah",
            [{"field": "oldPassword", "message": "Password lama salah"}],
        )
    if body.old_password == body.new_password:
        raise AppError(
            400,
            "BAD_REQUEST",
            "Password baru harus berbeda dari password lama",
            [{"field": "newPassword", "message": "Harus berbeda dari password lama"}],
        )

    await user_repo.update(
        db, user_id, {"passwordHash": await ahash_password(body.new_password), "updatedAt": utcnow()}
    )
    await audit.log(db, current, AuditAction.UPDATE, AuditModule.USER, user_id, "Mengganti password sendiri")
