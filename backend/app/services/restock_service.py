"""Restock + HPP moving average (dokumen 05 §5.3). Semua perubahan dalam SATU transaction."""

from datetime import date, datetime
from typing import Any

from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.core.enums import AuditAction, AuditModule
from app.core.errors import AppError, bad_request, not_found
from app.db.transaction import run_in_transaction
from app.repositories import product_repo, stock_movement_repo, supplier_repo, transaction_repository
from app.schemas.auth import CurrentUser
from app.schemas.restock import RestockCreate
from app.services import audit_service as audit
from app.services.code_service import next_code
from app.services.hpp import moving_average
from app.utils.objectid import optional_object_id, try_object_id
from app.utils.time import ensure_utc, utcnow, validate_date_order, wib_range_to_utc


async def create(
    db: AsyncDatabase, actor: CurrentUser, body: RestockCreate, at: datetime | None = None
) -> dict:
    """`at` hanya untuk skrip seed (dokumen 05 §9), tidak diekspos lewat API."""
    created_at = ensure_utc(at) if at else utcnow()

    ids = [item.product_id for item in body.items]
    dupes = [{"field": f"items[{i}].productId"} for i, pid in enumerate(ids) if pid in ids[:i]]
    if dupes:
        raise bad_request("Produk yang sama tidak boleh muncul dua kali dalam satu restock", dupes)

    supplier = await supplier_repo.find_by_id(db, ObjectId(body.supplier_id))
    if supplier is None:
        raise AppError(404, "NOT_FOUND", "Supplier tidak ditemukan", [{"field": "supplierId"}])
    if not supplier["isActive"]:
        raise bad_request("Supplier sedang nonaktif", [{"field": "supplierId"}])

    # Produk boleh nonaktif, tapi harus ada. Dicek dulu supaya pesan error menyebut semua item.
    found = {str(p["_id"]) for p in await product_repo.find_by_ids(db, [ObjectId(i) for i in ids])}
    missing = [
        {"field": f"items[{i}].productId", "productId": pid} for i, pid in enumerate(ids) if pid not in found
    ]
    if missing:
        raise AppError(404, "NOT_FOUND", "Ada produk yang tidak ditemukan", missing)

    creator = {"id": ObjectId(actor.id), "name": actor.name}

    async def txn(session) -> dict:
        restock_id = ObjectId()
        code = await next_code(db, "RST", session, at=created_at)
        lines: list[dict[str, Any]] = []
        movements: list[dict[str, Any]] = []
        for item in body.items:
            product = await product_repo.find_by_id(db, ObjectId(item.product_id), session)
            new_cost = moving_average(
                product["stock"], product["costPrice"], item.quantity, item.purchase_price
            )
            after = await product_repo.apply_restock(
                db, product["_id"], item.quantity, new_cost, item.purchase_price, created_at, session
            )
            movements.append(
                {
                    "productId": product["_id"],
                    "productName": product["name"],
                    "type": "RESTOCK",
                    "quantity": item.quantity,
                    "stockBefore": after["stock"] - item.quantity,
                    "stockAfter": after["stock"],
                    "referenceId": restock_id,
                    "referenceCode": code,
                    "createdBy": creator,
                    "createdAt": created_at,
                }
            )
            lines.append(
                {
                    "productId": product["_id"],
                    "sku": product["sku"],
                    "name": product["name"],
                    "unit": product["unit"],
                    "quantity": item.quantity,
                    "purchasePrice": item.purchase_price,
                    "subtotal": item.quantity * item.purchase_price,
                }
            )
        total = sum(line["subtotal"] for line in lines)
        doc = {
            "_id": restock_id,
            "code": code,
            "type": "RESTOCK",
            "status": "COMPLETED",
            "cashier": None,
            "customerName": None,
            "member": None,
            "supplier": {
                "id": supplier["_id"],
                "supplierCode": supplier["supplierCode"],
                "name": supplier["name"],
            },
            "items": lines,
            "subtotal": total,
            "discount": 0,
            "tax": 0,
            "total": total,
            "payment": None,
            "notes": body.notes,
            "createdBy": creator,
            "createdAt": created_at,
        }
        await stock_movement_repo.insert_many(db, movements, session)
        await transaction_repository.insert(db, doc, session)
        await audit.log(
            db,
            actor,
            AuditAction.RESTOCK,
            AuditModule.RESTOCK,
            restock_id,
            f"Restock {code} dari {supplier['name']} ({len(lines)} item)",
            session=session,
            at=created_at,
        )
        return doc

    return await run_in_transaction(db.client, txn)


async def list_restocks(
    db: AsyncDatabase,
    supplier_id: str | None,
    date_from: date | None,
    date_to: date | None,
    page: int,
    limit: int,
) -> tuple[list[dict], int]:
    validate_date_order(date_from, date_to)
    start, end = wib_range_to_utc(date_from, date_to)
    flt = transaction_repository.build_filter(
        tx_type="RESTOCK",
        start_utc=start,
        end_utc=end,
        supplier_id=optional_object_id(supplier_id, "supplierId"),
    )
    docs = await transaction_repository.find_page(db, flt, "-createdAt", (page - 1) * limit, limit)
    return docs, await transaction_repository.count(db, flt)


async def get_restock(db: AsyncDatabase, restock_id: str) -> dict:
    oid = try_object_id(restock_id)
    doc = await transaction_repository.find_by_id(db, oid) if oid else None
    if doc is None or doc.get("type") != "RESTOCK":
        raise not_found("Restock tidak ditemukan")
    return doc
