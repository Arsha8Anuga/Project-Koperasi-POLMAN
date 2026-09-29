"""Schema request untuk penjualan kasir (POST /sales)."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field, field_validator, model_validator

from app.core.enums import PaymentMethod
from app.schemas.common import CamelModel, RequestId


class PaymentIn(CamelModel):
    """Data pembayaran.

    CASH: amountPaid wajib. QRIS: amountPaid diabaikan, backend mengisinya dengan total.
    Bilangan dibuat ketat (strict) agar 15000.0 atau "15000" ditolak (BR-10).
    """

    method: PaymentMethod
    amount_paid: Annotated[int, Field(strict=True, ge=0)] | None = None

    @model_validator(mode="after")
    def cash_needs_amount(self) -> "PaymentIn":
        if self.method == PaymentMethod.CASH and self.amount_paid is None:
            raise ValueError("Uang yang diterima wajib diisi untuk pembayaran tunai")
        return self


class SaleItemIn(CamelModel):
    """Satu baris keranjang. Frontend tidak mengirim harga (BR-05)."""

    product_id: RequestId
    quantity: Annotated[int, Field(strict=True, ge=1, le=999)]


class SaleCreate(CamelModel):
    """Body POST /sales.

    Field lain yang dikirim frontend (misalnya price atau total) diabaikan.
    """

    items: list[SaleItemIn] = Field(min_length=1, max_length=50)
    customer_name: str | None = Field(default=None, max_length=60)
    member_id: RequestId | None = None
    payment: PaymentIn

    @field_validator("customer_name", mode="before")
    @classmethod
    def clean_customer_name(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

    @field_validator("member_id", mode="before")
    @classmethod
    def empty_member_id_is_none(cls, value):
        if isinstance(value, str) and not value.strip():
            return None
        return value
