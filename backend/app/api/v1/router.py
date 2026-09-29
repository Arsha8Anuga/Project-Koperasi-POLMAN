"""Semua router v1 didaftarkan di sini. BE-2/BE-3: tambahkan import + include_router
modul kalian di bagian masing-masing (satu baris per modul, supaya konflik merge kecil)."""

from fastapi import APIRouter

from app.api.v1 import audit_logs, auth, dashboard, members, users

api_router = APIRouter()

# --- BE-1 ---
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(members.router)
api_router.include_router(audit_logs.router)
api_router.include_router(dashboard.router)

# --- BE-2 --- (categories, products, suppliers, restocks, stock, reports/stock)

# --- BE-3 --- (sales, transactions, reports)
