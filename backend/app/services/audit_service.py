"""Audit trail (dokumen 05 §7). Dipanggil dari SERVICE, bukan router/middleware.

Pemakaian (BE-2 / BE-3):

    from app.services import audit_service as audit
    from app.core.enums import AuditAction, AuditModule

    await audit.log(db, user, AuditAction.UPDATE, AuditModule.PRODUCT, product["_id"],
                    f"Mengubah harga jual {sku} dari {old} menjadi {new}")

    # di dalam transaction: teruskan session, supaya log ikut di-rollback kalau gagal
    await audit.log(db, cashier, AuditAction.SALE, AuditModule.SALE, sale["_id"],
                    f"Penjualan {code}", session=session)

IP client diambil otomatis dari konteks request; tidak perlu diteruskan.
"""

from datetime import date, datetime
from typing import Any

from bson import ObjectId
from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.asynchronous.database import AsyncDatabase

from app.core.enums import AuditAction, AuditModule
from app.repositories import audit_log_repo
from app.schemas.audit_log import AuditLogOut
from app.schemas.auth import CurrentUser
from app.utils.objectid import optional_object_id
from app.utils.pagination import PageParams
from app.utils.request_context import client_ip
from app.utils.time import created_at_filter, utcnow


async def log(
    db: AsyncDatabase,
    actor: CurrentUser,
    action: AuditAction,
    module: AuditModule,
    reference_id: ObjectId | str | None,
    description: str,
    session: AsyncClientSession | None = None,
    at: datetime | None = None,  # hanya untuk skrip seed (dokumen 05 §9)
) -> None:
    if isinstance(reference_id, str):
        reference_id = ObjectId(reference_id)
    await audit_log_repo.insert(
        db,
        {
            "user": {"id": ObjectId(actor.id), "name": actor.name, "role": str(actor.role)},
            "action": str(action),
            "module": str(module),
            "referenceId": reference_id,
            "description": description,
            "ip": client_ip.get(),
            "createdAt": at or utcnow(),
        },
        session=session,
    )


async def list_logs(
    db: AsyncDatabase,
    page: PageParams,
    user_id: str | None = None,
    module: AuditModule | None = None,
    action: AuditAction | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> tuple[list[AuditLogOut], int]:
    filter: dict[str, Any] = {}
    if oid := optional_object_id(user_id, "userId"):
        filter["user.id"] = oid
    if module:
        filter["module"] = str(module)
    if action:
        filter["action"] = str(action)
    filter.update(created_at_filter(date_from, date_to))

    docs, total = await audit_log_repo.list_page(db, filter, page)
    return [AuditLogOut.model_validate(d) for d in docs], total
