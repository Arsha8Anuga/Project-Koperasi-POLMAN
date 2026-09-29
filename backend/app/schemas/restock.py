from pydantic import Field
from app.schemas.category import CamelModel

class RestockItem(CamelModel):
    product_id: str
    quantity: int = Field(ge=1, le=10000)
    purchase_price: int = Field(ge=0)

class RestockCreate(CamelModel):
    supplier_id: str
    items: list[RestockItem] = Field(min_length=1, max_length=50)
    notes: str | None = None