from datetime import date
from typing import Any

from pymongo.asynchronous.database import AsyncDatabase

from app.core.enums import StockMovementType, StockStatus
from app.repositories import category_repo, product_repo, stock_movement_repo
from app.schemas.stock import StockMovementOut, StockReport, StockReportItem
from app.services.product_service import stock_status
from app.utils.objectid import optional_object_id
from app.utils.pagination import PageParams
from app.utils.time import created_at_filter


async def list_movements(
    db: AsyncDatabase,
    page: PageParams,
    product_id: str | None,
    type_: StockMovementType | None,
    date_from: date | None,
    date_to: date | None,
) -> tuple[list[StockMovementOut], int]:
    filter: dict[str, Any] = created_at_filter(date_from, date_to)
    if pid := optional_object_id(product_id, "productId"):
        filter["productId"] = pid
    if type_:
        filter["type"] = str(type_)
    docs, total = await stock_movement_repo.list_page(db, filter, page)
    return [StockMovementOut.model_validate(d) for d in docs], total


async def stock_report(db: AsyncDatabase, category_id: str | None, status: StockStatus | None) -> StockReport:
    """Stok semua produk AKTIF. `counts` selalu dihitung dari semua status (filter status hanya
    memengaruhi `items`), supaya kartu ringkasan di frontend tidak ikut berubah."""
    filter: dict[str, Any] = {"isActive": True}
    if cat := optional_object_id(category_id, "categoryId"):
        filter["categoryId"] = cat
    names = await category_repo.name_map(db)
    counts = {"OK": 0, "LOW": 0, "OUT": 0}
    items: list[StockReportItem] = []
    for p in await product_repo.find_all(db, filter):
        s = stock_status(p["stock"], p["minimumStock"])
        counts[str(s)] += 1
        if status is None or s == status:
            items.append(
                StockReportItem(
                    product_id=p["_id"],
                    sku=p["sku"],
                    name=p["name"],
                    category_name=names.get(p["categoryId"]),
                    stock=p["stock"],
                    minimum_stock=p["minimumStock"],
                    stock_status=s,
                )
            )
    return StockReport(items=items, counts=counts)
