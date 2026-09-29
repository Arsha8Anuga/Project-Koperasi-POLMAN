"""Dashboard OWNER — milik BE-3. Angka "hari ini" memakai hari WIB."""

from pymongo.asynchronous.database import AsyncDatabase

from app.repositories import report_repository, transaction_repository
from app.schemas.dashboard import OwnerSummary
from app.utils.time import today_wib, wib_range_to_utc


async def owner_summary(db: AsyncDatabase) -> OwnerSummary:
    today = today_wib()
    start_utc, end_utc = wib_range_to_utc(today, today)

    cash_rows = await report_repository.cashflow_rows(db, start_utc, end_utc, "day")
    profit_rows = await report_repository.gross_profit_rows(db, start_utc, end_utc, "day")
    sales_filter = transaction_repository.build_filter(tx_type="SALE", start_utc=start_utc, end_utc=end_utc)

    return OwnerSummary(
        sales_today=sum(int(r["income"]) for r in cash_rows),
        transactions_today=await transaction_repository.count(db, sales_filter),
        gross_profit_today=sum(int(r["revenue"]) - int(r["cogs"]) for r in profit_rows),
        restock_today=sum(int(r["expense"]) for r in cash_rows),
    )
