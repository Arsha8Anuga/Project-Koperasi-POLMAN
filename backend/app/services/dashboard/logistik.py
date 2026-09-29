"""Dashboard LOGISTIK — milik BE-2."""

from pymongo.asynchronous.database import AsyncDatabase

from app.repositories import product_repo, transaction_repository
from app.schemas.dashboard import LogistikSummary
from app.utils.time import today_wib, wib_month_start_utc


async def logistik_summary(db: AsyncDatabase) -> LogistikSummary:
    counts = await product_repo.count_by_stock_status(db, {"isActive": True})
    restock_filter = transaction_repository.build_filter(
        tx_type="RESTOCK", start_utc=wib_month_start_utc(today_wib())
    )
    return LogistikSummary(
        active_products=sum(counts.values()),
        low_stock_count=counts["LOW"],
        out_of_stock_count=counts["OUT"],
        restocks_this_month=await transaction_repository.count(db, restock_filter),
    )
