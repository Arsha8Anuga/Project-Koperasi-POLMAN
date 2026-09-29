from fastapi import APIRouter, Depends, Query
from pymongo.asynchronous.database import AsyncDatabase

from app.api.deps import CurrentUser, get_db, require_roles
from app.core.enums import Role
from app.schemas.common import ERROR_RESPONSES, ApiResponse, PaginatedResponse
from app.schemas.supplier import SupplierCreate, SupplierOut, SupplierStatusUpdate, SupplierUpdate
from app.services import supplier_service
from app.utils.pagination import PageParams
from app.utils.response import ok, paginated

router = APIRouter(prefix="/suppliers", tags=["suppliers"], responses=ERROR_RESPONSES)
viewers = require_roles(Role.LOGISTIK, Role.OWNER)
logistik_only = require_roles(Role.LOGISTIK)


@router.get("", response_model=PaginatedResponse[SupplierOut])
async def list_suppliers(
    page: PageParams = Depends(),
    search: str | None = Query(None, max_length=64),
    is_active: bool | None = Query(None, alias="isActive"),
    _: CurrentUser = Depends(viewers),
    db: AsyncDatabase = Depends(get_db),
):
    items, total = await supplier_service.list_suppliers(db, page, search, is_active)
    return paginated(items, page, total)


@router.get("/{supplier_id}", response_model=ApiResponse[SupplierOut])
async def get_supplier(
    supplier_id: str, _: CurrentUser = Depends(viewers), db: AsyncDatabase = Depends(get_db)
):
    return ok(await supplier_service.get_supplier(db, supplier_id))


@router.post("", status_code=201, response_model=ApiResponse[SupplierOut])
async def create_supplier(
    body: SupplierCreate, user: CurrentUser = Depends(logistik_only), db: AsyncDatabase = Depends(get_db)
):
    return ok(await supplier_service.create(db, user, body), "Supplier berhasil dibuat")


@router.put("/{supplier_id}", response_model=ApiResponse[SupplierOut])
async def update_supplier(
    supplier_id: str,
    body: SupplierUpdate,
    user: CurrentUser = Depends(logistik_only),
    db: AsyncDatabase = Depends(get_db),
):
    return ok(await supplier_service.update(db, user, supplier_id, body), "Supplier berhasil diperbarui")


@router.patch("/{supplier_id}/status", response_model=ApiResponse[SupplierOut])
async def set_supplier_status(
    supplier_id: str,
    body: SupplierStatusUpdate,
    user: CurrentUser = Depends(logistik_only),
    db: AsyncDatabase = Depends(get_db),
):
    result = await supplier_service.set_status(db, user, supplier_id, body)
    return ok(
        result, "Supplier berhasil diaktifkan" if result.is_active else "Supplier berhasil dinonaktifkan"
    )
