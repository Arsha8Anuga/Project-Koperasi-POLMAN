from typing import Any

from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import DuplicateKeyError

from app.core.enums import AuditAction, AuditModule
from app.core.errors import duplicate, not_found
from app.repositories import member_repo
from app.schemas.auth import CurrentUser
from app.schemas.member import MemberCreate, MemberLookup, MemberOut, MemberUpdate
from app.services import audit_service as audit
from app.utils.objectid import parse_object_id
from app.utils.pagination import PageParams
from app.utils.text import search_regex
from app.utils.time import today_wib, utcnow

_NOT_FOUND = "Anggota tidak ditemukan"


async def list_members(
    db: AsyncDatabase, page: PageParams, search: str | None, is_active: bool | None
) -> tuple[list[MemberOut], int]:
    filter: dict[str, Any] = {}
    if search and search.strip():
        rx = search_regex(search)
        filter["$or"] = [{"name": rx}, {"memberNumber": rx}, {"phone": rx}]
    if is_active is not None:
        filter["isActive"] = is_active
    docs, total = await member_repo.list_page(db, filter, page)
    return [MemberOut.model_validate(d) for d in docs], total


async def _get_or_404(db: AsyncDatabase, member_id: str) -> dict:
    member = await member_repo.find_by_id(db, parse_object_id(member_id, _NOT_FOUND))
    if member is None:
        raise not_found(_NOT_FOUND)
    return member


async def get_member(db: AsyncDatabase, member_id: str) -> MemberOut:
    return MemberOut.model_validate(await _get_or_404(db, member_id))


async def lookup(db: AsyncDatabase, member_number: str) -> MemberLookup:
    """Untuk kasir. Anggota nonaktif diperlakukan sama dengan tidak ada."""
    member = await member_repo.find_active_by_number(db, member_number.strip().upper())
    if member is None:
        raise not_found("Nomor anggota tidak ditemukan atau tidak aktif")
    return MemberLookup(id=member["_id"], member_number=member["memberNumber"], name=member["name"])


async def create_member(db: AsyncDatabase, actor: CurrentUser, body: MemberCreate) -> MemberOut:
    now = utcnow()
    doc = {
        "memberNumber": body.member_number,
        "name": body.name,
        "phone": body.phone,
        "joinedAt": (body.joined_at or today_wib()).isoformat(),
        "isActive": True,
        "createdAt": now,
        "updatedAt": now,
    }
    try:
        doc = await member_repo.insert(db, doc)
    except DuplicateKeyError:
        raise duplicate(f"Nomor anggota '{body.member_number}' sudah dipakai", "memberNumber") from None
    await audit.log(
        db,
        actor,
        AuditAction.CREATE,
        AuditModule.MEMBER,
        doc["_id"],
        f"Mendaftarkan anggota {body.member_number} - {body.name}",
    )
    return MemberOut.model_validate(doc)


async def update_member(
    db: AsyncDatabase, actor: CurrentUser, member_id: str, body: MemberUpdate
) -> MemberOut:
    member = await _get_or_404(db, member_id)
    label = member["memberNumber"]

    changes = []
    if body.name != member["name"]:
        changes.append(f"nama dari '{member['name']}' menjadi '{body.name}'")
    if body.phone != member.get("phone"):
        changes.append(f"telepon dari {member.get('phone') or '-'} menjadi {body.phone or '-'}")
    status_changed = body.is_active != member["isActive"]
    if not changes and not status_changed:
        return MemberOut.model_validate(member)

    updated = await member_repo.update(
        db,
        member["_id"],
        {"name": body.name, "phone": body.phone, "isActive": body.is_active, "updatedAt": utcnow()},
    )
    # Satu entri audit per jenis aksi, supaya filter action=DEACTIVATE tetap berguna.
    if changes:
        await audit.log(
            db,
            actor,
            AuditAction.UPDATE,
            AuditModule.MEMBER,
            member["_id"],
            f"Mengubah {', '.join(changes)} pada anggota {label}",
        )
    if status_changed:
        action = AuditAction.ACTIVATE if body.is_active else AuditAction.DEACTIVATE
        verb = "Mengaktifkan" if body.is_active else "Menonaktifkan"
        await audit.log(db, actor, action, AuditModule.MEMBER, member["_id"], f"{verb} anggota {label}")
    return MemberOut.model_validate(updated)
