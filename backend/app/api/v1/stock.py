# app/api/v1/stock.py
from fastapi import APIRouter, Depends, Query  # type: ignore[reportMissingImports]
from app.api.deps import get_db, require_roles
from app.core.enums import Role
from app.services import stock_service
from app.utils.response import ok
from datetime import date
from typing import Literal
from app.utils.response import paginated

router = APIRouter(tags=["Stock"])      # tanpa prefix, path ditulis lengkap di bawah

@router.get("/stock/movements")
async def list_movements(product_id: str | None = Query(None, alias="productId"),
                         type: Literal["SALE", "RESTOCK"] | None = None,
                         date_from: date | None = Query(None, alias="from"),
                         date_to: date | None = Query(None, alias="to"),
                         page: int = Query(1, ge=1),
                         limit: int = Query(20, ge=1, le=100),
                         user=Depends(require_roles(Role.LOGISTIK, Role.OWNER)),
                         db=Depends(get_db)):
    items, total, limit = await stock_service.list_movements(
        db, product_id, type, date_from, date_to, page, limit)
    return paginated(items, page, limit, total)

@router.get("/reports/stock")
async def stock_report(category_id: str | None = Query(None, alias="categoryId"),
                       stock_status: str | None = Query(None, alias="stockStatus"),
                       user=Depends(require_roles(Role.LOGISTIK, Role.OWNER)),
                       db=Depends(get_db)):
    return ok(await stock_service.stock_report(db, category_id, stock_status))