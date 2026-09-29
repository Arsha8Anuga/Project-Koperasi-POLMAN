from fastapi import APIRouter, Depends, Query
from app.api.deps import get_db, require_roles
from app.core.enums import Role
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierStatus
from app.services import supplier_service
from app.utils.response import ok, paginated

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

VIEW = (Role.LOGISTIK, Role.OWNER)     # yang boleh lihat
EDIT = (Role.LOGISTIK,)                # yang boleh ubah


@router.get("")
async def list_suppliers(search: str | None = None,
                         is_active: bool | None = Query(None, alias="isActive"),
                         page: int = Query(1, ge=1),
                         limit: int = Query(20, ge=1, le=100),
                         user=Depends(require_roles(*VIEW)), db=Depends(get_db)):
    items, total, limit = await supplier_service.list_suppliers(db, search, is_active, page, limit)
    return paginated(
        items=items,
        page=page,
        total=total,
        message="OK"
    )


@router.get("/{id}")
async def get_supplier(id: str, user=Depends(require_roles(*VIEW)), db=Depends(get_db)):
    return ok(await supplier_service.get(db, id))


@router.post("", status_code=201)
async def create_supplier(body: SupplierCreate,
                          user=Depends(require_roles(*EDIT)), db=Depends(get_db)):
    return ok(await supplier_service.create(db, user, body), "Supplier berhasil dibuat")


@router.put("/{id}")
async def update_supplier(id: str, body: SupplierUpdate,
                          user=Depends(require_roles(*EDIT)), db=Depends(get_db)):
    return ok(await supplier_service.update(db, user, id, body), "Supplier berhasil diubah")


@router.patch("/{id}/status")
async def supplier_status(id: str, body: SupplierStatus,
                          user=Depends(require_roles(*EDIT)), db=Depends(get_db)):
    return ok(await supplier_service.set_status(db, user, id, body.is_active), "Status supplier diubah")