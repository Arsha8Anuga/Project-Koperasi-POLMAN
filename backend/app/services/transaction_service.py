"""Logika riwayat transaksi untuk Owner (SALE dan RESTOCK) serta pembentukan response."""

from __future__ import annotations

from datetime import date
from typing import Any

from app.core.enums import Role
from app.core.errors import AppError
from app.repositories import transaction_repository
from app.schemas.transaction import TransactionOut, TransactionSummary
from app.utils.objectid import optional_object_id, try_object_id
from app.utils.time import validate_date_order, wib_range_to_utc


def role_value(user: Any) -> str:
    """Ambil nama role sebagai string, baik role berupa Enum maupun string biasa."""
    role = getattr(user, "role", user)
    return str(getattr(role, "value", role))


def present(doc: dict, include_cost: bool) -> dict:
    """Ubah dokumen database menjadi JSON response (camelCase, id string, waktu UTC Z).

    Untuk KASIR, include_cost diisi False sehingga costPrice pada item dihilangkan.
    """
    model = TransactionOut.from_doc(doc)
    exclude = None if include_cost else {"items": {"__all__": {"cost_price"}}}
    return model.model_dump(by_alias=True, mode="json", exclude=exclude)


def present_for_user(doc: dict, user: Any) -> dict:
    return present(doc, include_cost=role_value(user) != Role.KASIR.value)


async def list_transactions(
    db,
    *,
    tx_type: str | None,
    from_date: date | None,
    to_date: date | None,
    cashier_id: str | None,
    supplier_id: str | None,
    member_id: str | None,
    search: str | None,
    sort: str,
    page: int,
    limit: int,
) -> tuple[list[dict], int, dict]:
    """Daftar transaksi dengan filter. Mengembalikan (dokumen, total, summary)."""
    if sort not in transaction_repository.SORT_OPTIONS:
        raise AppError(
            422,
            "VALIDATION_ERROR",
            "Pilihan urutan tidak valid",
            [
                {
                    "field": "sort",
                    "message": "Pilihan: " + ", ".join(transaction_repository.SORT_OPTIONS),
                }
            ],
        )
    validate_date_order(from_date, to_date)
    start_utc, end_utc = wib_range_to_utc(from_date, to_date)

    flt = transaction_repository.build_filter(
        tx_type=tx_type,
        start_utc=start_utc,
        end_utc=end_utc,
        cashier_id=optional_object_id(cashier_id, "cashierId"),
        supplier_id=optional_object_id(supplier_id, "supplierId"),
        member_id=optional_object_id(member_id, "memberId"),
        search=search,
    )
    docs = await transaction_repository.find_page(db, flt, sort, (page - 1) * limit, limit)
    total = await transaction_repository.count(db, flt)
    raw_summary = await transaction_repository.summarize(db, flt)
    summary = TransactionSummary(
        count=raw_summary["count"],
        total_sales=raw_summary["totalSales"],
        total_restock=raw_summary["totalRestock"],
    ).model_dump(by_alias=True)
    return docs, total, summary


async def get_transaction(db, transaction_id: str) -> dict:
    """Detail satu transaksi (SALE atau RESTOCK) untuk Owner."""
    oid = try_object_id(transaction_id)
    doc = await transaction_repository.find_by_id(db, oid) if oid else None
    if doc is None:
        raise AppError(404, "NOT_FOUND", "Transaksi tidak ditemukan")
    return doc
