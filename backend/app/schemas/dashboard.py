"""`GET /dashboard/summary` — isi `data` berbeda per role (dokumen 04 §7.2).
ADMIN = BE-1, LOGISTIK = BE-2, OWNER = BE-3. Masing-masing mengisi fungsi di
`app/services/dashboard/<role>.py`, router & dispatcher-nya milik BE-1."""

from pydantic import Field

from app.schemas.common import CamelModel


class AdminSummary(CamelModel):
    active_users: int
    users_by_role: dict[str, int] = Field(description='{"OWNER": 1, "LOGISTIK": 2, "ADMIN": 1, "KASIR": 5}')
    active_members: int
    audit_logs_today: int


class LogistikSummary(CamelModel):
    active_products: int
    low_stock_count: int
    out_of_stock_count: int
    restocks_this_month: int


class OwnerSummary(CamelModel):
    sales_today: int
    transactions_today: int
    gross_profit_today: int
    restock_today: int


# Urutan penting: Pydantic mencoba satu per satu, field-nya tidak saling tumpang tindih.
DashboardSummary = AdminSummary | LogistikSummary | OwnerSummary
