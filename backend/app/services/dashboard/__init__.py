"""`GET /dashboard/summary`: dispatcher per role. Router & dispatcher milik BE-1; isi tiap
fungsi milik pemilik role-nya, di file terpisah supaya tidak ada konflik merge:

    admin.py    → BE-1
    logistik.py → BE-2
    owner.py    → BE-3
"""

from pymongo.asynchronous.database import AsyncDatabase

from app.core.enums import Role
from app.core.errors import forbidden
from app.schemas.auth import CurrentUser
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard.admin import admin_summary
from app.services.dashboard.logistik import logistik_summary
from app.services.dashboard.owner import owner_summary

_HANDLERS = {
    Role.ADMIN: admin_summary,
    Role.LOGISTIK: logistik_summary,
    Role.OWNER: owner_summary,
}


async def get_summary(db: AsyncDatabase, user: CurrentUser) -> DashboardSummary:
    handler = _HANDLERS.get(user.role)
    if handler is None:  # KASIR — seharusnya sudah ditolak require_roles
        raise forbidden()
    return await handler(db)
