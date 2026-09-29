from app.repositories import supplier_repo
from app.schemas.supplier import SupplierOut
from app.utils.serialize import to_json
from app.utils.time import utcnow            # sesuaikan path
from app.services import audit_service as audit               # punya BE-1
from app.core.errors import AppError


def _out(doc: dict) -> dict:
    return SupplierOut.model_validate(to_json(doc)).model_dump(by_alias=True)


def _fields(body) -> dict:
    return {"supplierCode": body.supplier_code.strip().upper(), "name": body.name.strip(),
            "contactPerson": body.contact_person, "phone": body.phone,
            "email": body.email, "address": body.address, "notes": body.notes}


async def _get_or_404(db, id):
    doc = await supplier_repo.find_by_id(db, id)
    if not doc:
        raise AppError(404, "NOT_FOUND", "Supplier tidak ditemukan")
    return doc


async def list_suppliers(db, search, is_active, page, limit):
    limit = min(limit, 100)
    docs, total = await supplier_repo.find_page(db, search, is_active, (page - 1) * limit, limit)
    return [_out(d) for d in docs], total, limit


async def get(db, id):
    return _out(await _get_or_404(db, id))


async def create(db, user, body):
    now = utcnow()
    doc = {**_fields(body), "isActive": True, "createdAt": now, "updatedAt": now}
    doc = await supplier_repo.insert(db, doc)      # kode kembar → 409 DUPLICATE otomatis
    await audit.log(db, user, "CREATE", "SUPPLIER", doc["_id"], f"Membuat supplier {doc['supplierCode']}")
    return _out(doc)


async def update(db, user, id, body):
    await _get_or_404(db, id)
    doc = await supplier_repo.update(db, id, {**_fields(body), "updatedAt": utcnow()})
    await audit.log(db, user, "UPDATE", "SUPPLIER", doc["_id"], f"Mengubah supplier {doc['supplierCode']}")
    return _out(doc)


async def set_status(db, user, id, is_active: bool):
    await _get_or_404(db, id)
    doc = await supplier_repo.update(db, id, {"isActive": is_active, "updatedAt": utcnow()})
    action = "ACTIVATE" if is_active else "DEACTIVATE"
    await audit.log(db, user, action, "SUPPLIER", doc["_id"], f"{action.title()} supplier {doc['supplierCode']}")
    return _out(doc)