"""Router riwayat transaksi untuk Owner: /transactions."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUser, get_db, require_roles
from app.core.enums import Role, TransactionType
from app.schemas.common import ok_response, paged_response
from app.services import transaction_service

router = APIRouter(prefix="/transactions", tags=["Transactions"])


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
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
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
        page=page,
        limit=limit,
    )
    data = [transaction_service.present(doc, include_cost=True) for doc in docs]
    return paged_response(data, page, limit, total, summary=summary)


@router.get("/{transaction_id}", summary="Detail transaksi lengkap")
async def get_transaction(
    transaction_id: str,
    user: CurrentUser = Depends(require_roles(Role.OWNER)),
    db=Depends(get_db),
):
    doc = await transaction_service.get_transaction(db, transaction_id)
    return ok_response(transaction_service.present(doc, include_cost=True))
