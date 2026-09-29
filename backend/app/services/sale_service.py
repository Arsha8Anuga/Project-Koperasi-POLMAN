"""Logika bisnis penjualan kasir: checkout atomik, riwayat kasir, dan invoice."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from bson import ObjectId

from app.core.enums import PaymentMethod, Role
from app.core.errors import AppError
from app.repositories import checkout_repository, transaction_repository
from app.schemas.sale import PaymentIn, SaleCreate, SaleItemIn
from app.services import audit
from app.services.code_service import next_code
from app.services.transaction_runner import run_in_transaction
from app.services.transaction_service import role_value
from app.utils.datetime_utils import (
    date_bounds,
    ensure_utc,
    today_wib,
    utcnow,
    validate_date_order,
)
from app.utils.mongo_ids import parse_object_id


def format_rupiah(value: int) -> str:
    """Contoh: 10500 menjadi 'Rp 10.500'."""
    return "Rp " + f"{value:,}".replace(",", ".")


# ---------------------------------------------------------------------------
# Fungsi murni (tidak menyentuh database, mudah diuji)
# ---------------------------------------------------------------------------


def find_duplicate_items(items: list[SaleItemIn]) -> list[dict]:
    """Cari productId yang muncul lebih dari satu kali di keranjang."""
    seen: set[str] = set()
    duplicates: list[dict] = []
    for index, item in enumerate(items):
        key = item.product_id.lower()
        if key in seen:
            duplicates.append({"field": f"items[{index}].productId", "productId": item.product_id})
        seen.add(key)
    return duplicates


def check_products(items: list[SaleItemIn], products_by_id: dict[str, dict]) -> None:
    """Pemeriksaan awal: produk ada, aktif, dan stoknya cukup.

    Pemeriksaan ini hanya agar pesan error bisa menyebut semua item yang bermasalah sekaligus.
    Jaminan stok tidak minus datang dari update bersyarat di dalam transaction.
    """
    missing: list[dict] = []
    inactive: list[dict] = []
    shortages: list[dict] = []
    for index, item in enumerate(items):
        product = products_by_id.get(item.product_id.lower())
        if product is None:
            missing.append({"field": f"items[{index}].productId", "productId": item.product_id})
            continue
        if not product.get("isActive", True):
            inactive.append(
                {
                    "field": f"items[{index}].productId",
                    "productId": item.product_id,
                    "name": product.get("name"),
                }
            )
            continue
        available = int(product.get("stock", 0))
        if item.quantity > available:
            shortages.append(
                {
                    "field": f"items[{index}].quantity",
                    "productId": item.product_id,
                    "name": product.get("name"),
                    "requested": item.quantity,
                    "available": available,
                }
            )
    if missing:
        raise AppError(404, "NOT_FOUND", "Ada produk yang tidak ditemukan", missing)
    if inactive:
        raise AppError(409, "PRODUCT_INACTIVE", "Ada produk yang sudah tidak aktif", inactive)
    if shortages:
        raise AppError(409, "INSUFFICIENT_STOCK", "Stok tidak mencukupi", shortages)


def make_line(product: dict, quantity: int) -> dict:
    """Bentuk satu item transaksi berupa snapshot data produk saat ini (BR-03).

    Harga dan HPP diambil dari database, bukan dari frontend (BR-05).
    """
    price = int(product["sellingPrice"])
    return {
        "productId": product["_id"],
        "sku": product.get("sku", ""),
        "name": product.get("name", ""),
        "unit": product.get("unit") or "pcs",
        "quantity": quantity,
        "price": price,
        "costPrice": int(product.get("costPrice") or 0),
        "subtotal": price * quantity,
    }


def build_payment(payment: PaymentIn, total: int, paid_at: datetime) -> dict:
    """Terapkan aturan pembayaran BR-06.

    CASH: amountPaid harus >= total, kembalian = amountPaid - total.
    QRIS: amountPaid = total, kembalian = 0.
    """
    if payment.method == PaymentMethod.QRIS:
        return {
            "method": PaymentMethod.QRIS.value,
            "amountPaid": total,
            "change": 0,
            "paidAt": paid_at,
        }
    amount_paid = int(payment.amount_paid or 0)
    if amount_paid < total:
        raise AppError(
            422,
            "PAYMENT_INSUFFICIENT",
            "Uang yang diterima kurang dari total belanja",
            [{"field": "payment.amountPaid", "total": total, "amountPaid": amount_paid}],
        )
    return {
        "method": PaymentMethod.CASH.value,
        "amountPaid": amount_paid,
        "change": amount_paid - total,
        "paidAt": paid_at,
    }


# ---------------------------------------------------------------------------
# Checkout
# ---------------------------------------------------------------------------


async def _raise_stock_error(db, index: int, item: SaleItemIn, session) -> None:
    """Dipanggil ketika update stok bersyarat gagal. Cari tahu penyebabnya lalu lempar error."""
    product = await checkout_repository.find_product(db, ObjectId(item.product_id), session)
    if product is None:
        raise AppError(
            404,
            "NOT_FOUND",
            "Ada produk yang tidak ditemukan",
            [{"field": f"items[{index}].productId", "productId": item.product_id}],
        )
    if not product.get("isActive", True):
        raise AppError(
            409,
            "PRODUCT_INACTIVE",
            "Ada produk yang sudah tidak aktif",
            [
                {
                    "field": f"items[{index}].productId",
                    "productId": item.product_id,
                    "name": product.get("name"),
                }
            ],
        )
    raise AppError(
        409,
        "INSUFFICIENT_STOCK",
        "Stok tidak mencukupi",
        [
            {
                "field": f"items[{index}].quantity",
                "productId": item.product_id,
                "name": product.get("name"),
                "requested": item.quantity,
                "available": int(product.get("stock", 0)),
            }
        ],
    )


async def checkout(
    db, cashier: Any, body: SaleCreate, at: datetime | None = None
) -> dict:
    """Proses penjualan dari keranjang kasir. Mengembalikan dokumen transaksi SALE.

    Langkah:
    1. Validasi awal dan hitung ulang total dari harga di database.
    2. Buka MongoDB transaction.
    3. Per item: kurangi stok dengan update bersyarat (stok >= qty), catat stock movement.
    4. Buat kode TRX-YYYYMMDD-NNNN dari collection counters.
    5. Simpan dokumen transaksi dan audit log.
    6. Commit. Jika ada error di langkah mana pun, semuanya di-rollback.

    Parameter at hanya dipakai skrip seed dan tidak boleh diekspos lewat API.
    """
    created_at = ensure_utc(at) if at else utcnow()
    cashier_oid = parse_object_id(str(cashier.id))
    if cashier_oid is None:
        raise AppError(401, "UNAUTHORIZED", "Sesi tidak valid, silakan login ulang")

    # 1. Validasi awal
    duplicates = find_duplicate_items(body.items)
    if duplicates:
        raise AppError(
            400,
            "BAD_REQUEST",
            "Produk yang sama tidak boleh muncul dua kali di keranjang",
            duplicates,
        )

    product_ids = [ObjectId(item.product_id) for item in body.items]
    products = await checkout_repository.find_products_by_ids(db, product_ids)
    products_by_id = {str(product["_id"]): product for product in products}
    check_products(body.items, products_by_id)

    precheck_lines = [
        make_line(products_by_id[item.product_id.lower()], item.quantity) for item in body.items
    ]
    precheck_total = sum(line["subtotal"] for line in precheck_lines)
    build_payment(body.payment, precheck_total, created_at)  # uang kurang: berhenti lebih awal

    member_snapshot: dict | None = None
    if body.member_id:
        member = await checkout_repository.find_active_member(db, ObjectId(body.member_id))
        if member is None:
            raise AppError(
                404,
                "NOT_FOUND",
                "Anggota tidak ditemukan atau tidak aktif",
                [{"field": "memberId", "memberId": body.member_id}],
            )
        member_snapshot = {
            "id": member["_id"],
            "memberNumber": member.get("memberNumber", ""),
            "name": member.get("name", ""),
        }
    customer_name = body.customer_name or (member_snapshot["name"] if member_snapshot else None)

    # 2 sampai 6. Semua perubahan data terjadi di dalam satu transaction.
    async def work(session) -> dict:
        lines: list[dict] = []
        movements: list[dict] = []

        for index, item in enumerate(body.items):
            product_oid = ObjectId(item.product_id)
            updated = await checkout_repository.decrement_stock_if_available(
                db, product_oid, item.quantity, created_at, session
            )
            if updated is None:
                await _raise_stock_error(db, index, item, session)
            line = make_line(updated, item.quantity)
            lines.append(line)
            stock_after = int(updated["stock"])
            movements.append(
                {
                    "productId": product_oid,
                    "productName": line["name"],
                    "type": "SALE",
                    "quantity": -item.quantity,
                    "stockBefore": stock_after + item.quantity,
                    "stockAfter": stock_after,
                    "createdBy": {"id": cashier_oid, "name": cashier.name},
                    "createdAt": created_at,
                }
            )

        # Total dihitung dari harga yang benar-benar dipakai saat stok dikurangi.
        subtotal = sum(line["subtotal"] for line in lines)
        payment = build_payment(body.payment, subtotal, created_at)

        code = await next_code(db, "TRX", session, at=created_at)
        sale_id = ObjectId()
        for movement in movements:
            movement["referenceId"] = sale_id
            movement["referenceCode"] = code
        await checkout_repository.insert_movements(db, movements, session)

        sale = {
            "_id": sale_id,
            "code": code,
            "type": "SALE",
            "status": "COMPLETED",
            "cashier": {"id": cashier_oid, "name": cashier.name},
            "customerName": customer_name,
            "member": member_snapshot,
            "supplier": None,
            "items": lines,
            "subtotal": subtotal,
            "discount": 0,  # BR-12: tidak ada diskon dan pajak di MVP
            "tax": 0,
            "total": subtotal,
            "payment": payment,
            "notes": None,
            "createdBy": {"id": cashier_oid, "name": cashier.name},
            "createdAt": created_at,
        }
        await transaction_repository.insert(db, sale, session)
        await audit.log(
            db,
            cashier,
            "SALE",
            "SALE",
            sale_id,
            f"Penjualan {code} dengan total {format_rupiah(subtotal)}",
            session,
        )
        return sale

    return await run_in_transaction(db, work)


# ---------------------------------------------------------------------------
# Riwayat dan invoice
# ---------------------------------------------------------------------------


async def list_my_sales(
    db,
    cashier: Any,
    from_date: date | None,
    to_date: date | None,
    page: int,
    limit: int,
) -> tuple[list[dict], int]:
    """Riwayat penjualan milik kasir yang login. Bawaan: hari ini (WIB)."""
    validate_date_order(from_date, to_date)
    end_date = to_date or today_wib()
    start_date = from_date or end_date
    validate_date_order(start_date, end_date)
    start_utc, end_utc = date_bounds(start_date, end_date)

    cashier_oid = parse_object_id(str(cashier.id))
    flt = transaction_repository.build_filter(
        tx_type="SALE",
        start_utc=start_utc,
        end_utc=end_utc,
        cashier_id=cashier_oid,
    )
    docs = await transaction_repository.find_page(db, flt, "-createdAt", (page - 1) * limit, limit)
    total = await transaction_repository.count(db, flt)
    return docs, total


async def get_sale_for_user(db, sale_id: str, user: Any) -> dict:
    """Ambil satu transaksi penjualan untuk invoice.

    KASIR hanya boleh membuka transaksinya sendiri. OWNER boleh membuka semuanya.
    """
    oid = parse_object_id(sale_id)
    doc = await transaction_repository.find_by_id(db, oid) if oid else None
    if doc is None or doc.get("type") != "SALE":
        raise AppError(404, "NOT_FOUND", "Transaksi tidak ditemukan")
    if role_value(user) == Role.KASIR.value:
        owner_id = str((doc.get("cashier") or {}).get("id", ""))
        if owner_id != str(user.id):
            raise AppError(403, "FORBIDDEN", "Anda tidak memiliki akses ke transaksi ini")
    return doc
