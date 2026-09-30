from typing import Any

from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import DuplicateKeyError

from app.core.enums import AuditAction, AuditModule
from app.core.errors import duplicate, not_found
from app.repositories import counter_repository, member_repo
from app.schemas.auth import CurrentUser
from app.schemas.member import MemberCreate, MemberLookup, MemberOut, MemberUpdate
from app.services import audit_service as audit
from app.utils.objectid import parse_object_id
from app.utils.pagination import PageParams
from app.utils.text import search_regex
from app.utils.time import today_wib, utcnow

_NOT_FOUND = "Anggota tidak ditemukan"

MEMBER_PREFIX = "KOP"
_COUNTER_KEY = "MEMBER"
_NUMBER_PATTERN = rf"^{MEMBER_PREFIX}-[0-9]+$"
_MAX_ATTEMPTS = 5


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


async def _sync_counter(db: AsyncDatabase, force: bool = False) -> None:
    """Counter anggota harus >= nomor terbesar yang sudah ada (data lama / seed diinsert tanpa counter).
    Normalnya hanya dihitung kalau counter belum ada; `force` dipakai setelah bentrok nomor."""
    if not force and await counter_repository.exists(db, _COUNTER_KEY):
        return
    numbers = await member_repo.member_numbers_matching(db, _NUMBER_PATTERN)
    highest = max((int(n.split("-", 1)[1]) for n in numbers), default=0)
    await counter_repository.ensure_at_least(db, _COUNTER_KEY, highest)


async def next_member_number(db: AsyncDatabase) -> str:
    """KOP-001, KOP-002, ... (lebar minimal 3 digit, bertambah sendiri setelah KOP-999)."""
    await _sync_counter(db)
    seq = await counter_repository.increment(db, _COUNTER_KEY)
    return f"{MEMBER_PREFIX}-{seq:03d}"


async def create_member(db: AsyncDatabase, actor: CurrentUser, body: MemberCreate) -> MemberOut:
    """Dipakai ADMIN dan KASIR. Nomor anggota selalu dibuat di sini, tidak pernah dari client."""
    now = utcnow()
    for _ in range(_MAX_ATTEMPTS):
        number = await next_member_number(db)
        doc = {
            "memberNumber": number,
            "name": body.name,
            "phone": body.phone,
            "joinedAt": (body.joined_at or today_wib()).isoformat(),
            "isActive": True,
            "createdAt": now,
            "updatedAt": now,
        }
        try:
            doc = await member_repo.insert(db, doc)
            break
        except DuplicateKeyError:
            # Nomor sudah dipakai data yang diinsert di luar counter (seed / impor manual):
            # selaraskan counter dengan nomor terbesar, lalu coba lagi.
            await _sync_counter(db, force=True)
    else:
        raise duplicate("Gagal membuat nomor anggota unik, coba lagi", "memberNumber")

    await audit.log(
        db,
        actor,
        AuditAction.CREATE,
        AuditModule.MEMBER,
        doc["_id"],
        f"Mendaftarkan anggota {number} - {body.name} (oleh {actor.role.value})",
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
