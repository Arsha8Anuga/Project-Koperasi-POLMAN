"""Semua router v1 didaftarkan di sini. Tambah modul baru = satu baris import + satu include_router
di bagian pemiliknya (supaya konflik merge kecil)."""

from fastapi import APIRouter

from app.api.v1 import (
    audit_logs,
    auth,
    categories,
    dashboard,
    insights,
    members,
    products,
    reports,
    restocks,
    sales,
    stock,
    suppliers,
    transactions,
    users,
)

api_router = APIRouter()

# --- BE-1 ---
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(members.router)
api_router.include_router(audit_logs.router)
api_router.include_router(dashboard.router)

# --- BE-2 ---
api_router.include_router(categories.router)
api_router.include_router(products.router)
api_router.include_router(suppliers.router)
api_router.include_router(restocks.router)
api_router.include_router(stock.router)  # /stock/movements + /reports/stock

# --- BE-3 ---
api_router.include_router(sales.router)
api_router.include_router(transactions.router)
api_router.include_router(reports.router)

# --- AI engine (hasil dibaca dari collection insights) ---
api_router.include_router(insights.router)
