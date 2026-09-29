# app/schemas/product.py  (import CamelModel dari schemas/category atau punya BE-1)
from datetime import datetime

from pydantic import Field
from app.schemas.category import CamelModel


class ProductCreate(CamelModel):
    sku: str = Field(min_length=1, max_length=40)
    barcode: str | None = None
    name: str = Field(min_length=1, max_length=120)
    category_id: str
    unit: str = Field(min_length=1, max_length=20)
    selling_price: int = Field(ge=0)          # integer, BUKAN float (BR-10)
    minimum_stock: int = Field(ge=0, default=0)
    image_url: str | None = None

ProductUpdate = ProductCreate                  # body PUT sama dengan POST

class ProductStatus(CamelModel):
    is_active: bool

class ProductOut(CamelModel):
    id: str; sku: str; barcode: str | None = None; name: str
    category_id: str; category_name: str | None = None; unit: str
    selling_price: int; cost_price: int; last_purchase_price: int
    stock: int; minimum_stock: int; stock_status: str
    image_url: str | None = None; is_active: bool
    created_at: datetime; updated_at: datetime      # from datetime import datetime