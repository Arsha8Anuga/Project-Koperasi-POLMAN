from fastapi import APIRouter, Depends, Query
from pymongo.asynchronous.database import AsyncDatabase

from app.api.deps import CurrentUser, get_db, require_roles
from app.core.enums import Role
from app.schemas.common import ERROR_RESPONSES, ApiResponse, PaginatedResponse
from app.schemas.user import PasswordReset, UserCreate, UserOut, UserStatusUpdate, UserUpdate
from app.services import user_service
from app.utils.pagination import PageParams
from app.utils.response import ok, paginated

router = APIRouter(prefix="/users", tags=["users"], responses=ERROR_RESPONSES)
admin_only = require_roles(Role.ADMIN)


@router.get("", response_model=PaginatedResponse[UserOut])
async def list_users(
    page: PageParams = Depends(),
    search: str | None = Query(None, max_length=64),
    role: Role | None = None,
    is_active: bool | None = Query(None, alias="isActive"),
    _: CurrentUser = Depends(admin_only),
    db: AsyncDatabase = Depends(get_db),
):
    items, total = await user_service.list_users(db, page, search, role, is_active)
    return paginated(items, page, total)


@router.post("", status_code=201, response_model=ApiResponse[UserOut])
async def create_user(
    body: UserCreate, user: CurrentUser = Depends(admin_only), db: AsyncDatabase = Depends(get_db)
):
    return ok(await user_service.create_user(db, user, body), "User berhasil dibuat")


@router.get("/{user_id}", response_model=ApiResponse[UserOut])
async def get_user(user_id: str, _: CurrentUser = Depends(admin_only), db: AsyncDatabase = Depends(get_db)):
    return ok(await user_service.get_user(db, user_id))


@router.put("/{user_id}", response_model=ApiResponse[UserOut])
async def update_user(
    user_id: str,
    body: UserUpdate,
    user: CurrentUser = Depends(admin_only),
    db: AsyncDatabase = Depends(get_db),
):
    return ok(await user_service.update_user(db, user, user_id, body), "User berhasil diperbarui")


@router.patch("/{user_id}/status", response_model=ApiResponse[UserOut])
async def set_status(
    user_id: str,
    body: UserStatusUpdate,
    user: CurrentUser = Depends(admin_only),
    db: AsyncDatabase = Depends(get_db),
):
    result = await user_service.set_status(db, user, user_id, body)
    return ok(result, "User berhasil diaktifkan" if result.is_active else "User berhasil dinonaktifkan")


@router.post("/{user_id}/reset-password", response_model=ApiResponse[None])
async def reset_password(
    user_id: str,
    body: PasswordReset,
    user: CurrentUser = Depends(admin_only),
    db: AsyncDatabase = Depends(get_db),
):
    await user_service.reset_password(db, user, user_id, body)
    return ok(None, "Password berhasil direset")
