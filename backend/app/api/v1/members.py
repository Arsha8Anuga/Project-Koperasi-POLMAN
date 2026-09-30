from fastapi import APIRouter, Depends, Query
from pymongo.asynchronous.database import AsyncDatabase

from app.api.deps import CurrentUser, get_db, require_roles
from app.core.enums import Role
from app.schemas.common import ERROR_RESPONSES, ApiResponse, PaginatedResponse
from app.schemas.member import MemberCreate, MemberLookup, MemberOut, MemberUpdate
from app.services import member_service
from app.utils.pagination import PageParams
from app.utils.response import ok, paginated

router = APIRouter(prefix="/members", tags=["members"], responses=ERROR_RESPONSES)
admin_only = require_roles(Role.ADMIN)


@router.get("", response_model=PaginatedResponse[MemberOut])
async def list_members(
    page: PageParams = Depends(),
    search: str | None = Query(None, max_length=64),
    is_active: bool | None = Query(None, alias="isActive"),
    _: CurrentUser = Depends(admin_only),
    db: AsyncDatabase = Depends(get_db),
):
    items, total = await member_service.list_members(db, page, search, is_active)
    return paginated(items, page, total)


@router.post("", status_code=201, response_model=ApiResponse[MemberOut])
async def create_member(
    body: MemberCreate,
    user: CurrentUser = Depends(require_roles(Role.ADMIN, Role.KASIR)),
    db: AsyncDatabase = Depends(get_db),
):
    """KASIR boleh mendaftarkan anggota; ubah data & nonaktifkan tetap khusus ADMIN.
    Nomor anggota dibuat otomatis (KOP-NNN)."""
    return ok(await member_service.create_member(db, user, body), "Anggota berhasil didaftarkan")


# Didefinisikan SEBELUM /{member_id} supaya "lookup" tidak dianggap sebagai ID.
@router.get("/lookup/{member_number}", response_model=ApiResponse[MemberLookup])
async def lookup_member(
    member_number: str,
    _: CurrentUser = Depends(require_roles(Role.KASIR, Role.ADMIN)),
    db: AsyncDatabase = Depends(get_db),
):
    return ok(await member_service.lookup(db, member_number))


@router.get("/{member_id}", response_model=ApiResponse[MemberOut])
async def get_member(
    member_id: str, _: CurrentUser = Depends(admin_only), db: AsyncDatabase = Depends(get_db)
):
    return ok(await member_service.get_member(db, member_id))


@router.put("/{member_id}", response_model=ApiResponse[MemberOut])
async def update_member(
    member_id: str,
    body: MemberUpdate,
    user: CurrentUser = Depends(admin_only),
    db: AsyncDatabase = Depends(get_db),
):
    return ok(await member_service.update_member(db, user, member_id, body), "Anggota berhasil diperbarui")
