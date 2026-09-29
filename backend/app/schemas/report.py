"""Schema response laporan owner (dokumen 04 §7.12)."""

from __future__ import annotations

from datetime import date

from pydantic import Field

from app.core.enums import Granularity
from app.schemas.common import CamelModel, IdStr


class CashflowBucket(CamelModel):
    period: str
    income: int
    expense: int
    net: int


class CashflowTotals(CamelModel):
    income: int
    expense: int
    net: int


class CashflowReport(CamelModel):
    granularity: Granularity
    from_date: date = Field(alias="from")
    to_date: date = Field(alias="to")
    buckets: list[CashflowBucket]
    totals: CashflowTotals


class GrossProfitBucket(CamelModel):
    period: str
    revenue: int
    cogs: int
    gross_profit: int
    margin: float


class GrossProfitTotals(CamelModel):
    revenue: int
    cogs: int
    gross_profit: int
    margin: float


class GrossProfitReport(CamelModel):
    granularity: Granularity
    from_date: date = Field(alias="from")
    to_date: date = Field(alias="to")
    buckets: list[GrossProfitBucket]
    totals: GrossProfitTotals


class BestSellerItem(CamelModel):
    rank: int
    product_id: IdStr
    sku: str
    name: str
    quantity_sold: int
    revenue: int


class BestSellerReport(CamelModel):
    from_date: date = Field(alias="from")
    to_date: date = Field(alias="to")
    items: list[BestSellerItem]
