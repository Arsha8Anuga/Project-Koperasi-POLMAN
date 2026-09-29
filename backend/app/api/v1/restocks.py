from datetime import date

from fastapi import APIRouter, Depends, Query
from pymongo.asynchronous.database import AsyncDatabase

from app.api.deps import CurrentUser, get_db, require_roles
from app.core.enums import Role
from app.schemas.common import ERROR_RESPONSES
from app.schemas.restock import RestockCreate
from app.services import restock_service
from app.services.transaction_service import present
from app.utils.pagination import PageParams
from app.utils.response import ok, paginated

router = APIRouter(prefix="/restocks", tags=["restocks"], responses=ERROR_RESPONSES)


@router.post("", status_code=201)
async def create_restock(
    body: RestockCreate,
    user: CurrentUser = Depends(require_roles(Role.LOGISTIK)),
    db: AsyncDatabase = Depends(get_db),
):
    doc = await restock_service.create(db, user, body)
    return ok(present(doc, include_cost=True), "Restock berhasil disimpan")


@router.get("")
async def list_restocks(
    page: PageParams = Depends(),
    supplier_id: str | None = Query(None, alias="supplierId"),
    date_from: date | None = Query(None, alias="from"),
    date_to: date | None = Query(None, alias="to"),
    _: CurrentUser = Depends(require_roles(Role.LOGISTIK)),
    db: AsyncDatabase = Depends(get_db),
):
    docs, total = await restock_service.list_restocks(
        db, supplier_id, date_from, date_to, page.page, page.limit
    )
    return paginated([present(d, include_cost=True) for d in docs], page, total)


@router.get("/{restock_id}")
async def get_restock(
    restock_id: str,
    _: CurrentUser = Depends(require_roles(Role.LOGISTIK, Role.OWNER)),
    db: AsyncDatabase = Depends(get_db),
):
    return ok(present(await restock_service.get_restock(db, restock_id), include_cost=True))
