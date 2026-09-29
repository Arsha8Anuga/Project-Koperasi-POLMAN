"""Router laporan Owner: /reports/cashflow, /reports/gross-profit, /reports/best-sellers.

Catatan: /reports/stock milik BE-2 dan dipasang di router terpisah.
"""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUser, get_db, require_roles
from app.core.enums import Granularity, Role
from app.schemas.common import ok_response
from app.services import report_service

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/cashflow", summary="Arus kas: pemasukan penjualan dan pengeluaran restock")
async def cashflow(
    granularity: Granularity = Query(default=Granularity.DAY),
    date_from: date | None = Query(default=None, alias="from"),
    date_to: date | None = Query(default=None, alias="to"),
    user: CurrentUser = Depends(require_roles(Role.OWNER)),
    db=Depends(get_db),
):
    return ok_response(await report_service.cashflow(db, granularity, date_from, date_to))


@router.get("/gross-profit", summary="Laba kotor: pendapatan dikurangi HPP")
async def gross_profit(
    granularity: Granularity = Query(default=Granularity.DAY),
    date_from: date | None = Query(default=None, alias="from"),
    date_to: date | None = Query(default=None, alias="to"),
    user: CurrentUser = Depends(require_roles(Role.OWNER)),
    db=Depends(get_db),
):
    return ok_response(await report_service.gross_profit(db, granularity, date_from, date_to))


@router.get("/best-sellers", summary="Produk terlaris berdasarkan jumlah terjual")
async def best_sellers(
    date_from: date | None = Query(default=None, alias="from"),
    date_to: date | None = Query(default=None, alias="to"),
    limit: int = Query(default=10, ge=1, le=100),
    category_id: str | None = Query(default=None, alias="categoryId"),
    user: CurrentUser = Depends(require_roles(Role.OWNER)),
    db=Depends(get_db),
):
    return ok_response(
        await report_service.best_sellers(db, date_from, date_to, limit, category_id)
    )
