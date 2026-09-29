from fastapi import APIRouter, Depends, Query
from pymongo.asynchronous.database import AsyncDatabase

from app.api.deps import CurrentUser, get_db, require_roles
from app.core.enums import Role
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.schemas.common import ERROR_RESPONSES, ApiResponse
from app.services import category_service
from app.utils.response import ok

router = APIRouter(prefix="/categories", tags=["categories"], responses=ERROR_RESPONSES)
logistik_only = require_roles(Role.LOGISTIK)


@router.get("", response_model=ApiResponse[list[CategoryOut]])
async def list_categories(
    is_active: bool | None = Query(None, alias="isActive"),
    _: CurrentUser = Depends(require_roles(Role.KASIR, Role.LOGISTIK, Role.OWNER)),
    db: AsyncDatabase = Depends(get_db),
):
    """Tanpa pagination (jumlah kategori kecil)."""
    return ok(await category_service.list_categories(db, is_active))


@router.post("", status_code=201, response_model=ApiResponse[CategoryOut])
async def create_category(
    body: CategoryCreate, user: CurrentUser = Depends(logistik_only), db: AsyncDatabase = Depends(get_db)
):
    return ok(await category_service.create(db, user, body), "Kategori berhasil dibuat")


@router.put("/{category_id}", response_model=ApiResponse[CategoryOut])
async def update_category(
    category_id: str,
    body: CategoryUpdate,
    user: CurrentUser = Depends(logistik_only),
    db: AsyncDatabase = Depends(get_db),
):
    return ok(await category_service.update(db, user, category_id, body), "Kategori berhasil diperbarui")
