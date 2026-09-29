"""`/stock/movements` dan `/reports/stock` (milik BE-2). Laporan lain di `reports.py` (BE-3)."""

from datetime import date

from fastapi import APIRouter, Depends, Query
from pymongo.asynchronous.database import AsyncDatabase

from app.api.deps import CurrentUser, get_db, require_roles
from app.core.enums import Role, StockMovementType, StockStatus
from app.schemas.common import ERROR_RESPONSES, ApiResponse, PaginatedResponse
from app.schemas.stock import StockMovementOut, StockReport
from app.services import stock_service
from app.utils.pagination import PageParams
from app.utils.response import ok, paginated

router = APIRouter(tags=["stock"], responses=ERROR_RESPONSES)
viewers = require_roles(Role.LOGISTIK, Role.OWNER)


@router.get("/stock/movements", response_model=PaginatedResponse[StockMovementOut])
async def list_movements(
    page: PageParams = Depends(),
    product_id: str | None = Query(None, alias="productId"),
    type: StockMovementType | None = None,
    date_from: date | None = Query(None, alias="from"),
    date_to: date | None = Query(None, alias="to"),
    _: CurrentUser = Depends(viewers),
    db: AsyncDatabase = Depends(get_db),
):
    items, total = await stock_service.list_movements(db, page, product_id, type, date_from, date_to)
    return paginated(items, page, total)


@router.get("/reports/stock", response_model=ApiResponse[StockReport])
async def stock_report(
    category_id: str | None = Query(None, alias="categoryId"),
    stock_status: StockStatus | None = Query(None, alias="stockStatus"),
    _: CurrentUser = Depends(viewers),
    db: AsyncDatabase = Depends(get_db),
):
    return ok(await stock_service.stock_report(db, category_id, stock_status))
