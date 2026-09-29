from typing import Any

from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import DuplicateKeyError

from app.core.enums import AuditAction, AuditModule, Role
from app.core.errors import bad_request, duplicate, not_found
from app.core.security import ahash_password
from app.repositories import user_repo
from app.schemas.auth import CurrentUser
from app.schemas.user import PasswordReset, UserCreate, UserOut, UserStatusUpdate, UserUpdate
from app.services import audit_service as audit
from app.utils.objectid import parse_object_id
from app.utils.pagination import PageParams
from app.utils.text import search_regex
from app.utils.time import utcnow

_NOT_FOUND = "User tidak ditemukan"


async def list_users(
    db: AsyncDatabase, page: PageParams, search: str | None, role: Role | None, is_active: bool | None
) -> tuple[list[UserOut], int]:
    filter: dict[str, Any] = {}
    if search and search.strip():
        rx = search_regex(search)
        filter["$or"] = [{"name": rx}, {"username": rx}]
    if role:
        filter["role"] = str(role)
    if is_active is not None:
        filter["isActive"] = is_active
    docs, total = await user_repo.list_page(db, filter, page)
    return [UserOut.model_validate(d) for d in docs], total


async def _get_or_404(db: AsyncDatabase, user_id: str) -> dict:
    user = await user_repo.find_by_id(db, parse_object_id(user_id, _NOT_FOUND))
    if user is None:
        raise not_found(_NOT_FOUND)
    return user


async def get_user(db: AsyncDatabase, user_id: str) -> UserOut:
    return UserOut.model_validate(await _get_or_404(db, user_id))


async def create_user(db: AsyncDatabase, actor: CurrentUser, body: UserCreate) -> UserOut:
    if await user_repo.find_by_username(db, body.username):
        raise duplicate(f"Username '{body.username}' sudah dipakai", "username")
    now = utcnow()
    doc = {
        "name": body.name,
        "username": body.username,
        "passwordHash": await ahash_password(body.password),
        "role": body.role,
        "isActive": True,
        "createdAt": now,
        "updatedAt": now,
    }
    try:
        doc = await user_repo.insert(db, doc)
    except DuplicateKeyError:  # dua request bersamaan lolos cek di atas
        raise duplicate(f"Username '{body.username}' sudah dipakai", "username") from None
    await audit.log(
        db,
        actor,
        AuditAction.CREATE,
        AuditModule.USER,
        doc["_id"],
        f"Membuat user {body.username} ({body.role})",
    )
    return UserOut.model_validate(doc)


async def update_user(db: AsyncDatabase, actor: CurrentUser, user_id: str, body: UserUpdate) -> UserOut:
    user = await _get_or_404(db, user_id)
    if str(user["_id"]) == actor.id and body.role != user["role"]:
        raise bad_request("Anda tidak dapat mengubah role akun sendiri")

    changes = []
    if body.name != user["name"]:
        changes.append(f"nama dari '{user['name']}' menjadi '{body.name}'")
    if body.role != user["role"]:
        changes.append(f"role dari {user['role']} menjadi {body.role}")
    if not changes:
        return UserOut.model_validate(user)

    updated = await user_repo.update(
        db, user["_id"], {"name": body.name, "role": body.role, "updatedAt": utcnow()}
    )
    await audit.log(
        db,
        actor,
        AuditAction.UPDATE,
        AuditModule.USER,
        user["_id"],
        f"Mengubah {', '.join(changes)} pada user {user['username']}",
    )
    return UserOut.model_validate(updated)


async def set_status(db: AsyncDatabase, actor: CurrentUser, user_id: str, body: UserStatusUpdate) -> UserOut:
    user = await _get_or_404(db, user_id)
    if str(user["_id"]) == actor.id and not body.is_active:
        raise bad_request("Anda tidak dapat menonaktifkan akun sendiri")
    if user["isActive"] == body.is_active:
        return UserOut.model_validate(user)

    updated = await user_repo.update(db, user["_id"], {"isActive": body.is_active, "updatedAt": utcnow()})
    action = AuditAction.ACTIVATE if body.is_active else AuditAction.DEACTIVATE
    verb = "Mengaktifkan" if body.is_active else "Menonaktifkan"
    await audit.log(db, actor, action, AuditModule.USER, user["_id"], f"{verb} user {user['username']}")
    return UserOut.model_validate(updated)


async def reset_password(db: AsyncDatabase, actor: CurrentUser, user_id: str, body: PasswordReset) -> None:
    user = await _get_or_404(db, user_id)
    await user_repo.update(
        db, user["_id"], {"passwordHash": await ahash_password(body.new_password), "updatedAt": utcnow()}
    )
    await audit.log(
        db,
        actor,
        AuditAction.RESET_PASSWORD,
        AuditModule.USER,
        user["_id"],
        f"Reset password user {user['username']}",
    )
