from datetime import date
from fastapi import APIRouter, Depends, Query  # type: ignore[reportMissingImports]
from app.api.deps import get_db, require_roles        # + get_client kalau ada
from app.core.enums import Role
from app.schemas.restock import RestockCreate
from app.services import restock_service
from app.utils.response import ok, paginated
from app.api.deps import get_client       


router = APIRouter(prefix="/restocks", tags=["Restocks"])


@router.post("", status_code=201)
async def create_restock(body: RestockCreate,
                         user=Depends(require_roles(Role.LOGISTIK)),
                         db=Depends(get_db),
                         client=Depends(get_client)):          # ← lihat catatan di bawah
    return ok(await restock_service.create(db, client, user, body), "Restock berhasil disimpan")


@router.get("")
async def list_restocks(supplier_id: str | None = Query(None, alias="supplierId"),
                        date_from: date | None = Query(None, alias="from"),
                        date_to: date | None = Query(None, alias="to"),
                        page: int = Query(1, ge=1),
                        limit: int = Query(20, ge=1, le=100),
                        user=Depends(require_roles(Role.LOGISTIK)), db=Depends(get_db)):
    items, total, limit = await restock_service.list_restocks(
        db, supplier_id, date_from, date_to, page, limit)
    return paginated(items, page, limit, total)


@router.get("/{id}")
async def get_restock(id: str, user=Depends(require_roles(Role.LOGISTIK, Role.OWNER)),
                      db=Depends(get_db)):
    return ok(await restock_service.get_restock(db, id))