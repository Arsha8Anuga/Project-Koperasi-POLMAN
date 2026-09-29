from typing import Annotated

from pydantic import Field, field_validator

from app.schemas.common import CamelModel, RequestId


class RestockItemIn(CamelModel):
    product_id: RequestId
    quantity: Annotated[int, Field(strict=True, ge=1, le=10_000)]
    purchase_price: Annotated[int, Field(strict=True, ge=0)]


class RestockCreate(CamelModel):
    supplier_id: RequestId
    items: list[RestockItemIn] = Field(min_length=1, max_length=50)
    notes: str | None = Field(default=None, max_length=300)

    @field_validator("notes", mode="before")
    @classmethod
    def _clean(cls, v):
        if isinstance(v, str):
            v = v.strip()
            return v or None
        return v
