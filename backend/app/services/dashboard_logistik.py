from datetime import datetime, timezone
from app.repositories import product_repo, restock_repo
from app.services.product_service import stock_status
from app.services.restock_service import WIB


async def summary(db) -> dict:
    products = await product_repo.find_active(db)
    statuses = [stock_status(p["stock"], p["minimumStock"]) for p in products]

    # awal bulan ini jam 00:00 WIB → UTC
    now_wib = datetime.now(WIB)
    month_start = now_wib.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_start_utc = month_start.astimezone(timezone.utc)

    return {
        "activeProducts": len(products),
        "lowStockCount": statuses.count("LOW"),
        "outOfStockCount": statuses.count("OUT"),
        "restocksThisMonth": await restock_repo.count_since(db, month_start_utc),
    }