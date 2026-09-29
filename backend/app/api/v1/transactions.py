"""Router riwayat transaksi untuk Owner: /transactions."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUser, get_db, require_roles
from app.core.enums import Role, TransactionType
from app.schemas.common import ERROR_RESPONSES
from app.services import transaction_service
from app.utils.pagination import PageParams
from app.utils.response import ok, paginated

router = APIRouter(prefix="/transactions", tags=["transactions"], responses=ERROR_RESPONSES)


@router.get("", summary="Riwayat transaksi SALE dan RESTOCK")
async def list_transactions(
    tx_type: TransactionType | None = Query(default=None, alias="type"),
    date_from: date | None = Query(default=None, alias="from"),
    date_to: date | None = Query(default=None, alias="to"),
    cashier_id: str | None = Query(default=None, alias="cashierId"),
    supplier_id: str | None = Query(default=None, alias="supplierId"),
    member_id: str | None = Query(default=None, alias="memberId"),
    search: str | None = Query(default=None, max_length=60),
    sort: str = Query(default="-createdAt"),
    page: PageParams = Depends(),
    user: CurrentUser = Depends(require_roles(Role.OWNER)),
    db=Depends(get_db),
):
    docs, total, summary = await transaction_service.list_transactions(
        db,
        tx_type=tx_type.value if tx_type else None,
        from_date=date_from,
        to_date=date_to,
        cashier_id=cashier_id,
        supplier_id=supplier_id,
        member_id=member_id,
        search=search,
        sort=sort,
        page=page.page,
        limit=page.limit,
    )
    data = [transaction_service.present(doc, include_cost=True) for doc in docs]
    return paginated(data, page, total, summary=summary)


@router.get("/{transaction_id}", summary="Detail transaksi lengkap")
async def get_transaction(
    transaction_id: str,
    user: CurrentUser = Depends(require_roles(Role.OWNER)),
    db=Depends(get_db),
):
    doc = await transaction_service.get_transaction(db, transaction_id)
    return ok(transaction_service.present(doc, include_cost=True))
