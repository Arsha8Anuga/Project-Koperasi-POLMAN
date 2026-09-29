"""Schema response transaksi (SALE dan RESTOCK) sesuai dokumen 04 bagian 5."""

from __future__ import annotations

from typing import Any

from pydantic import model_serializer

from app.schemas.common import CamelModel, IdStr, UtcDatetime


class ActorOut(CamelModel):
    """Snapshot pelaku: kasir atau pembuat transaksi."""

    id: IdStr
    name: str


class MemberRefOut(CamelModel):
    id: IdStr
    member_number: str
    name: str


class SupplierRefOut(CamelModel):
    id: IdStr
    supplier_code: str
    name: str


class TransactionItemOut(CamelModel):
    """Item transaksi.

    SALE memakai price dan costPrice. RESTOCK memakai purchasePrice.
    Kunci yang tidak dipakai (bernilai None) tidak ikut dikirim.
    """

    product_id: IdStr
    sku: str
    name: str
    unit: str = "pcs"
    quantity: int
    price: int | None = None
    cost_price: int | None = None
    purchase_price: int | None = None
    subtotal: int

    @model_serializer(mode="wrap")
    def drop_unused_price_keys(self, handler: Any) -> dict:
        data = handler(self)
        for key in ("price", "costPrice", "purchasePrice", "cost_price", "purchase_price"):
            if key in data and data[key] is None:
                del data[key]
        return data


class PaymentOut(CamelModel):
    method: str
    amount_paid: int
    change: int
    paid_at: UtcDatetime


class TransactionOut(CamelModel):
    id: IdStr
    code: str
    type: str
    status: str
    cashier: ActorOut | None = None
    customer_name: str | None = None
    member: MemberRefOut | None = None
    supplier: SupplierRefOut | None = None
    items: list[TransactionItemOut]
    subtotal: int
    discount: int = 0
    tax: int = 0
    total: int
    payment: PaymentOut | None = None
    notes: str | None = None
    created_by: ActorOut
    created_at: UtcDatetime

    @classmethod
    def from_doc(cls, doc: dict) -> TransactionOut:
        """Buat objek dari dokumen MongoDB (kunci _id diubah menjadi id)."""
        data = dict(doc)
        data["id"] = str(data.pop("_id"))
        return cls.model_validate(data)


class TransactionSummary(CamelModel):
    """Ringkasan untuk GET /transactions (sejajar dengan meta)."""

    count: int
    total_sales: int
    total_restock: int
