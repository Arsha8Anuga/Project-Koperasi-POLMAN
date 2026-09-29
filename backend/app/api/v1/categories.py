from fastapi import APIRouter, Depends, Query
from app.api.deps import get_db, require_roles      # sesuaikan import
from app.core.enums import Role
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.services import category_service
from app.utils.response import ok

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("")
async def list_categories(is_active: bool | None = Query(None, alias="isActive"),
                          user=Depends(require_roles(Role.KASIR, Role.LOGISTIK, Role.OWNER)),
                          db=Depends(get_db)):
    return ok(await category_service.list_all(db, is_active))

@router.post("", status_code=201)
async def create_category(body: CategoryCreate,
                          user=Depends(require_roles(Role.LOGISTIK)), db=Depends(get_db)):
    return ok(await category_service.create(db, user, body), "Kategori berhasil dibuat")

@router.put("/{id}")
async def update_category(id: str, body: CategoryUpdate,
                          user=Depends(require_roles(Role.LOGISTIK)), db=Depends(get_db)):
    return ok(await category_service.update(db, user, id, body), "Kategori berhasil diubah")