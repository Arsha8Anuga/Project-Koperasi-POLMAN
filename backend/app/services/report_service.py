"""Logika laporan owner: arus kas, laba kotor, dan produk terlaris.

Definisi (SRS bagian 5, wajib konsisten):
- Arus kas   = total SALE dikurangi total RESTOCK pada periode. Ini bukan laba.
- Laba kotor = jumlah (quantity x (price - costPrice)) semua item SALE pada periode.
"""

from __future__ import annotations

from datetime import date, timedelta

from app.core.enums import Granularity
from app.core.errors import AppError
from app.repositories import report_repository
from app.schemas.report import (
    BestSellerItem,
    BestSellerReport,
    CashflowBucket,
    CashflowReport,
    CashflowTotals,
    GrossProfitBucket,
    GrossProfitReport,
    GrossProfitTotals,
)
from app.utils.objectid import optional_object_id
from app.utils.time import today_wib, validate_date_order, wib_range_to_utc

# Batas rentang agar response tidak terlalu besar.
MAX_RANGE_DAYS = 3660


# ---------------------------------------------------------------------------
# Fungsi murni untuk tanggal dan label periode
# ---------------------------------------------------------------------------


def add_months(day: date, months: int) -> date:
    """Geser tanggal sekian bulan, hasilnya selalu tanggal 1."""
    index = day.year * 12 + (day.month - 1) + months
    return date(index // 12, index % 12 + 1, 1)


def default_start(granularity: Granularity, end: date) -> date:
    """Tanggal awal bawaan bila from tidak dikirim (mengikuti dokumen 06 bagian 5.4).

    day: 30 hari, week: 12 minggu, month: 12 bulan, year: 5 tahun.
    """
    if granularity == Granularity.DAY:
        return end - timedelta(days=29)
    if granularity == Granularity.WEEK:
        monday = end - timedelta(days=end.weekday())
        return monday - timedelta(weeks=11)
    if granularity == Granularity.MONTH:
        return add_months(end, -11)
    return date(end.year - 4, 1, 1)


def resolve_period(
    granularity: Granularity, from_date: date | None, to_date: date | None
) -> tuple[date, date]:
    """Tentukan rentang tanggal final (WIB, inklusif) dan periksa kewajarannya."""
    validate_date_order(from_date, to_date)
    end = to_date or today_wib()
    start = from_date or default_start(granularity, end)
    validate_date_order(start, end)
    if (end - start).days > MAX_RANGE_DAYS:
        raise AppError(
            422,
            "VALIDATION_ERROR",
            "Rentang tanggal terlalu panjang",
            [{"field": "from", "message": f"Rentang maksimal {MAX_RANGE_DAYS} hari"}],
        )
    return start, end


def period_labels(granularity: Granularity, start: date, end: date) -> list[str]:
    """Buat daftar label periode dari start sampai end, tanpa ada yang bolong.

    Format label sama dengan response dokumen 04 bagian 7.12:
    day YYYY-MM-DD, week YYYY-MM-DD (hari Senin), month YYYY-MM, year YYYY.
    """
    labels: list[str] = []
    if granularity == Granularity.DAY:
        current = start
        while current <= end:
            labels.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)
    elif granularity == Granularity.WEEK:
        current = start - timedelta(days=start.weekday())
        while current <= end:
            labels.append(current.strftime("%Y-%m-%d"))
            current += timedelta(weeks=1)
    elif granularity == Granularity.MONTH:
        current = date(start.year, start.month, 1)
        while current <= end:
            labels.append(current.strftime("%Y-%m"))
            current = add_months(current, 1)
    else:
        for year in range(start.year, end.year + 1):
            labels.append(str(year))
    return labels


def compute_margin(gross_profit: int, revenue: int) -> float:
    """Margin = laba kotor / pendapatan, dibulatkan 4 desimal. Nol jika pendapatan nol."""
    if revenue <= 0:
        return 0.0
    return round(gross_profit / revenue, 4)


# ---------------------------------------------------------------------------
# Laporan
# ---------------------------------------------------------------------------


async def cashflow(db, granularity: Granularity, from_date: date | None, to_date: date | None) -> dict:
    start, end = resolve_period(granularity, from_date, to_date)
    start_utc, end_utc = wib_range_to_utc(start, end)
    rows = await report_repository.cashflow_rows(db, start_utc, end_utc, granularity.value)
    by_label = {row["_id"]: row for row in rows}

    buckets: list[CashflowBucket] = []
    total_income = 0
    total_expense = 0
    for label in period_labels(granularity, start, end):
        row = by_label.get(label, {})
        income = int(row.get("income", 0))
        expense = int(row.get("expense", 0))
        total_income += income
        total_expense += expense
        buckets.append(CashflowBucket(period=label, income=income, expense=expense, net=income - expense))

    report = CashflowReport(
        granularity=granularity,
        from_date=start,
        to_date=end,
        buckets=buckets,
        totals=CashflowTotals(income=total_income, expense=total_expense, net=total_income - total_expense),
    )
    return report.model_dump(by_alias=True, mode="json")


async def gross_profit(db, granularity: Granularity, from_date: date | None, to_date: date | None) -> dict:
    start, end = resolve_period(granularity, from_date, to_date)
    start_utc, end_utc = wib_range_to_utc(start, end)
    rows = await report_repository.gross_profit_rows(db, start_utc, end_utc, granularity.value)
    by_label = {row["_id"]: row for row in rows}

    buckets: list[GrossProfitBucket] = []
    total_revenue = 0
    total_cogs = 0
    for label in period_labels(granularity, start, end):
        row = by_label.get(label, {})
        revenue = int(row.get("revenue", 0))
        cogs = int(row.get("cogs", 0))
        profit = revenue - cogs
        total_revenue += revenue
        total_cogs += cogs
        buckets.append(
            GrossProfitBucket(
                period=label,
                revenue=revenue,
                cogs=cogs,
                gross_profit=profit,
                margin=compute_margin(profit, revenue),
            )
        )

    total_profit = total_revenue - total_cogs
    report = GrossProfitReport(
        granularity=granularity,
        from_date=start,
        to_date=end,
        buckets=buckets,
        totals=GrossProfitTotals(
            revenue=total_revenue,
            cogs=total_cogs,
            gross_profit=total_profit,
            margin=compute_margin(total_profit, total_revenue),
        ),
    )
    return report.model_dump(by_alias=True, mode="json")


async def best_sellers(
    db,
    from_date: date | None,
    to_date: date | None,
    limit: int,
    category_id: str | None,
) -> dict:
    """Produk terlaris. Bawaan rentang 30 hari terakhir."""
    start, end = resolve_period(Granularity.DAY, from_date, to_date)
    start_utc, end_utc = wib_range_to_utc(start, end)

    product_ids = None
    if category_id:
        category_oid = optional_object_id(category_id, "categoryId")
        product_ids = await report_repository.find_product_ids_by_category(db, category_oid)

    rows = await report_repository.best_seller_rows(db, start_utc, end_utc, limit, product_ids)
    items = [
        BestSellerItem(
            rank=position,
            product_id=row["_id"],
            sku=row.get("sku", ""),
            name=row.get("name", ""),
            quantity_sold=int(row["quantitySold"]),
            revenue=int(row["revenue"]),
        )
        for position, row in enumerate(rows, start=1)
    ]
    report = BestSellerReport(from_date=start, to_date=end, items=items)
    return report.model_dump(by_alias=True, mode="json")
