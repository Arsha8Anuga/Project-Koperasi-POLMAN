# app/services/restock_service.py
from bson import ObjectId
from pymongo import ReturnDocument
from app.services.hpp import moving_average
from datetime import date, datetime, time, timedelta, timezone
from app.repositories import restock_repo
from app.utils.serialize import to_json
from app.core.errors import AppError
from app.services import audit_service as audit
# next_code punya BE-3; sesuaikan path importnya

WIB = timezone(timedelta(hours=7))     # WIB = UTC+7 tetap, tanpa perlu library tambahan


def _range_utc(date_from: date | None, date_to: date | None):
    """Tanggal WIB dari user → rentang UTC. Batas atas eksklusif (to + 1 hari)."""
    start = datetime.combine(date_from, time.min, tzinfo=WIB).astimezone(timezone.utc) if date_from else None
    end = (datetime.combine(date_to + timedelta(days=1), time.min, tzinfo=WIB)
           .astimezone(timezone.utc)) if date_to else None
    return start, end

async def list_restocks(db, supplier_id, date_from, date_to, page, limit):
    limit = min(limit, 100)
    start, end = _range_utc(date_from, date_to)
    docs, total = await restock_repo.find_page(db, supplier_id, start, end, (page - 1) * limit, limit)
    return [to_json(d) for d in docs], total, limit


async def get_restock(db, id):
    doc = await restock_repo.find_by_id(db, id)
    if not doc:
        raise AppError(404, "NOT_FOUND", "Restock tidak ditemukan")
    return to_json(doc)

async def create(db, client, user, body, at=None):
    at = at or utcnow()                       # 'at' hanya untuk skrip seed (dokumen 05 §9)
    ids = [i.product_id for i in body.items]
    if len(set(ids)) != len(ids):
        raise AppError(400, "BAD_REQUEST", "Produk tidak boleh duplikat dalam satu restock")

    supplier = await supplier_repo.find_by_id(db, body.supplier_id)
    if not supplier or not supplier["isActive"]:
        raise AppError(404, "NOT_FOUND", "Supplier tidak ditemukan atau nonaktif")

    async def txn(session):
        restock_id = ObjectId()
        code = await next_code(db, "RST", session)      # RST-20260928-0001
        lines, total = [], 0
        for it in body.items:
            p = await db.products.find_one({"_id": to_oid(it.product_id)}, session=session)
            if not p:
                raise AppError(404, "NOT_FOUND", "Produk tidak ditemukan")
            new_cost = moving_average(p["stock"], p["costPrice"], it.quantity, it.purchase_price)
            after = await db.products.find_one_and_update(
                {"_id": p["_id"]},
                {"$inc": {"stock": it.quantity},
                 "$set": {"costPrice": new_cost, "lastPurchasePrice": it.purchase_price,
                          "updatedAt": at}},
                return_document=ReturnDocument.AFTER, session=session)
            await db.stock_movements.insert_one({
                "productId": p["_id"], "productName": p["name"], "type": "RESTOCK",
                "quantity": it.quantity, "stockBefore": p["stock"], "stockAfter": after["stock"],
                "referenceId": restock_id, "referenceCode": code,
                "createdBy": {"id": ObjectId(user.id), "name": user.name}, "createdAt": at},
                session=session)
            subtotal = it.quantity * it.purchase_price
            total += subtotal
            lines.append({"productId": p["_id"], "sku": p["sku"], "name": p["name"],
                          "unit": p["unit"], "quantity": it.quantity,
                          "purchasePrice": it.purchase_price, "subtotal": subtotal})

        doc = {"_id": restock_id, "code": code, "type": "RESTOCK", "status": "COMPLETED",
               "cashier": None, "customerName": None, "member": None,
               "supplier": {"id": supplier["_id"], "supplierCode": supplier["supplierCode"],
                            "name": supplier["name"]},
               "items": lines, "subtotal": total, "discount": 0, "tax": 0, "total": total,
               "payment": None, "notes": body.notes,
               "createdBy": {"id": ObjectId(user.id), "name": user.name}, "createdAt": at}
        await db.transactions.insert_one(doc, session=session)
        await audit.log(db, user, "RESTOCK", "RESTOCK", restock_id, f"Restock {code}", session)
        return doc

    async with client.start_session() as session:
        doc = await session.with_transaction(txn)
    return to_json(doc)