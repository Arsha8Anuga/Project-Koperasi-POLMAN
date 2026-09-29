"""Router ringkasan dashboard: GET /dashboard/summary.

Isi response tergantung role. Fungsi ringkasan tiap role didaftarkan lewat
register_summary_provider() di app/services/dashboard_service.py. BE-3 mengisi OWNER.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, get_db, require_roles
from app.core.enums import Role
from app.schemas.common import ok_response
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", summary="Ringkasan dashboard sesuai role")
async def summary(
    user: CurrentUser = Depends(require_roles(Role.OWNER, Role.LOGISTIK, Role.ADMIN)),
    db=Depends(get_db),
):
    return ok_response(await dashboard_service.get_summary(db, user))
