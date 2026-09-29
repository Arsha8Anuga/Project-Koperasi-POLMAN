from app.core.enums import StockMovementType, StockStatus
from app.schemas.common import CamelModel, DocModel, ObjectIdStr, UtcDatetime
from app.schemas.transaction import ActorOut


class StockMovementOut(DocModel):
    product_id: ObjectIdStr
    product_name: str
    type: StockMovementType
    quantity: int
    stock_before: int
    stock_after: int
    reference_code: str
    reference_id: ObjectIdStr
    created_by: ActorOut
    created_at: UtcDatetime


class StockReportItem(CamelModel):
    product_id: ObjectIdStr
    sku: str
    name: str
    category_name: str | None = None
    stock: int
    minimum_stock: int
    stock_status: StockStatus


class StockReport(CamelModel):
    items: list[StockReportItem]
    counts: dict[str, int]
