"""Ringkasan dashboard.

Endpoint GET /dashboard/summary dipakai tiga role dengan isi berbeda, dan dikerjakan tiga orang.
Supaya tidak ada dua router untuk path yang sama, tiap role mendaftarkan fungsi ringkasannya
ke sini. BE-3 mendaftarkan OWNER. BE-1 mendaftarkan ADMIN dan BE-2 mendaftarkan LOGISTIK:

    from app.services.dashboard_service import register_summary_provider
    register_summary_provider(Role.ADMIN, admin_summary)   # async def admin_summary(db) -> dict
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from app.core.enums import Role
from app.core.errors import AppError
from app.repositories import report_repository, transaction_repository
from app.schemas.report import OwnerDashboardSummary
from app.services.transaction_service import role_value
from app.utils.datetime_utils import today_wib, wib_range_to_utc

SummaryProvider = Callable[[Any], Awaitable[dict]]

_providers: dict[str, SummaryProvider] = {}


def register_summary_provider(role: Any, provider: SummaryProvider) -> None:
    """Daftarkan fungsi ringkasan untuk satu role. Provider menerima db dan mengembalikan dict."""
    _providers[str(getattr(role, "value", role))] = provider


async def get_summary(db, user: Any) -> dict:
    provider = _providers.get(role_value(user))
    if provider is None:
        raise AppError(
            501,
            "NOT_IMPLEMENTED",
            "Ringkasan dashboard untuk role ini belum tersedia",
        )
    return await provider(db)


async def owner_summary(db) -> dict:
    """Angka utama hari ini (hari menurut WIB) untuk Owner."""
    today = today_wib()
    start_utc, end_utc = wib_range_to_utc(today, today)

    cash_rows = await report_repository.cashflow_rows(db, start_utc, end_utc, "day")
    profit_rows = await report_repository.gross_profit_rows(db, start_utc, end_utc, "day")
    sales_flt = transaction_repository.build_filter(
        tx_type="SALE", start_utc=start_utc, end_utc=end_utc
    )
    transactions_today = await transaction_repository.count(db, sales_flt)

    sales_today = sum(int(row["income"]) for row in cash_rows)
    restock_today = sum(int(row["expense"]) for row in cash_rows)
    profit_today = sum(int(row["revenue"]) - int(row["cogs"]) for row in profit_rows)

    summary = OwnerDashboardSummary(
        sales_today=sales_today,
        transactions_today=transactions_today,
        gross_profit_today=profit_today,
        restock_today=restock_today,
        net_cashflow_today=sales_today - restock_today,
    )
    return summary.model_dump(by_alias=True)


register_summary_provider(Role.OWNER, owner_summary)
