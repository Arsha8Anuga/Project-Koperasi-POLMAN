from typing import Annotated

from pydantic import Field, field_validator

from app.core.enums import StockStatus
from app.schemas.common import CamelModel, DocModel, ObjectIdStr, RequestId, UtcDatetime

# Uang & jumlah: integer ketat. 4000.5 atau "4000" ditolak (BR-10).
Money = Annotated[int, Field(strict=True, ge=0)]


def _clean(v):
    if isinstance(v, str):
        v = v.strip()
        return v or None
    return v


class ProductOut(DocModel):
    """Objek Product (dokumen 04 §5). `costPrice` & `lastPurchasePrice` dihapus untuk KASIR."""

    sku: str
    barcode: str | None = None
    name: str
    category_id: ObjectIdStr
    category_name: str | None = None
    unit: str
    selling_price: int
    cost_price: int
    last_purchase_price: int
    stock: int
    minimum_stock: int
    stock_status: StockStatus
    image_url: str | None = None
    is_active: bool
    created_at: UtcDatetime
    updated_at: UtcDatetime


class ProductCreate(CamelModel):
    """Body POST dan PUT. Field stock/costPrice/lastPurchasePrice kalau dikirim DIABAIKAN."""

    sku: str = Field(min_length=1, max_length=40)
    barcode: str | None = Field(default=None, max_length=40)
    name: str = Field(min_length=1, max_length=120)
    category_id: RequestId
    unit: str = Field(min_length=1, max_length=20)
    selling_price: Money
    minimum_stock: Annotated[int, Field(strict=True, ge=0)] = 0
    image_url: str | None = Field(default=None, max_length=500)

    _c = field_validator("sku", "barcode", "name", "unit", "image_url", mode="before")(_clean)

    @field_validator("sku")
    @classmethod
    def _upper(cls, v: str) -> str:
        return v.upper()


ProductUpdate = ProductCreate


class ProductStatusUpdate(CamelModel):
    is_active: bool
