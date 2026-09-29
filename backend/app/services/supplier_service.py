from typing import Any

from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import DuplicateKeyError

from app.core.enums import AuditAction, AuditModule
from app.core.errors import duplicate, not_found
from app.repositories import supplier_repo
from app.schemas.auth import CurrentUser
from app.schemas.supplier import SupplierCreate, SupplierOut, SupplierStatusUpdate, SupplierUpdate
from app.services import audit_service as audit
from app.utils.objectid import parse_object_id
from app.utils.pagination import PageParams
from app.utils.text import search_regex
from app.utils.time import utcnow

_NOT_FOUND = "Supplier tidak ditemukan"


def _fields(body: SupplierCreate) -> dict[str, Any]:
    return {
        "supplierCode": body.supplier_code,
        "name": body.name,
        "contactPerson": body.contact_person,
        "phone": body.phone,
        "email": body.email,
        "address": body.address,
        "notes": body.notes,
    }


async def _get_or_404(db: AsyncDatabase, supplier_id: str) -> dict[str, Any]:
    doc = await supplier_repo.find_by_id(db, parse_object_id(supplier_id, _NOT_FOUND))
    if doc is None:
        raise not_found(_NOT_FOUND)
    return doc


async def list_suppliers(
    db: AsyncDatabase, page: PageParams, search: str | None, is_active: bool | None
) -> tuple[list[SupplierOut], int]:
    filter: dict[str, Any] = {}
    if is_active is not None:
        filter["isActive"] = is_active
    if search and search.strip():
        rx = search_regex(search)
        filter["$or"] = [{"name": rx}, {"supplierCode": rx}, {"contactPerson": rx}]
    docs, total = await supplier_repo.list_page(db, filter, page)
    return [SupplierOut.model_validate(d) for d in docs], total


async def get_supplier(db: AsyncDatabase, supplier_id: str) -> SupplierOut:
    return SupplierOut.model_validate(await _get_or_404(db, supplier_id))


async def create(db: AsyncDatabase, actor: CurrentUser, body: SupplierCreate) -> SupplierOut:
    now = utcnow()
    doc = {**_fields(body), "isActive": True, "createdAt": now, "updatedAt": now}
    try:
        doc = await supplier_repo.insert(db, doc)
    except DuplicateKeyError:
        raise duplicate(f"Kode supplier '{body.supplier_code}' sudah dipakai", "supplierCode") from None
    await audit.log(
        db,
        actor,
        AuditAction.CREATE,
        AuditModule.SUPPLIER,
        doc["_id"],
        f"Membuat supplier {body.supplier_code} - {body.name}",
    )
    return SupplierOut.model_validate(doc)


async def update(
    db: AsyncDatabase, actor: CurrentUser, supplier_id: str, body: SupplierUpdate
) -> SupplierOut:
    old = await _get_or_404(db, supplier_id)
    try:
        doc = await supplier_repo.update(db, old["_id"], {**_fields(body), "updatedAt": utcnow()})
    except DuplicateKeyError:
        raise duplicate(f"Kode supplier '{body.supplier_code}' sudah dipakai", "supplierCode") from None
    await audit.log(
        db,
        actor,
        AuditAction.UPDATE,
        AuditModule.SUPPLIER,
        old["_id"],
        f"Mengubah supplier {old['supplierCode']}",
    )
    return SupplierOut.model_validate(doc)


async def set_status(
    db: AsyncDatabase, actor: CurrentUser, supplier_id: str, body: SupplierStatusUpdate
) -> SupplierOut:
    old = await _get_or_404(db, supplier_id)
    if old["isActive"] == body.is_active:
        return SupplierOut.model_validate(old)
    doc = await supplier_repo.update(db, old["_id"], {"isActive": body.is_active, "updatedAt": utcnow()})
    action = AuditAction.ACTIVATE if body.is_active else AuditAction.DEACTIVATE
    verb = "Mengaktifkan" if body.is_active else "Menonaktifkan"
    await audit.log(
        db, actor, action, AuditModule.SUPPLIER, old["_id"], f"{verb} supplier {old['supplierCode']}"
    )
    return SupplierOut.model_validate(doc)
