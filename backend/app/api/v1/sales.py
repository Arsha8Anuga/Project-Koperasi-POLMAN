"""Router penjualan kasir: /sales."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUser, get_db, require_roles
from app.core.enums import Role
from app.schemas.common import ok_response, paged_response
from app.schemas.sale import SaleCreate
from app.services import sale_service, transaction_service

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.post("", status_code=201, summary="Checkout penjualan")
async def create_sale(
    body: SaleCreate,
    user: CurrentUser = Depends(require_roles(Role.KASIR)),
    db=Depends(get_db),
):
    sale = await sale_service.checkout(db, user, body)
    return ok_response(
        transaction_service.present(sale, include_cost=False),
        "Transaksi berhasil disimpan",
    )


# Route /mine harus ditulis sebelum /{sale_id}, kalau tidak "mine" dianggap sebagai id.
@router.get("/mine", summary="Riwayat penjualan kasir yang login")
async def list_my_sales(
    date_from: date | None = Query(default=None, alias="from"),
    date_to: date | None = Query(default=None, alias="to"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    user: CurrentUser = Depends(require_roles(Role.KASIR)),
    db=Depends(get_db),
):
    docs, total = await sale_service.list_my_sales(db, user, date_from, date_to, page, limit)
    data = [transaction_service.present(doc, include_cost=False) for doc in docs]
    return paged_response(data, page, limit, total)


@router.get("/{sale_id}", summary="Detail transaksi untuk invoice")
async def get_sale(
    sale_id: str,
    user: CurrentUser = Depends(require_roles(Role.KASIR, Role.OWNER)),
    db=Depends(get_db),
):
    doc = await sale_service.get_sale_for_user(db, sale_id, user)
    return ok_response(transaction_service.present_for_user(doc, user))
