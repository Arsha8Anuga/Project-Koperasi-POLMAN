"""Dashboard ADMIN — BE-1."""

from pymongo.asynchronous.database import AsyncDatabase

from app.core.enums import STAFF_ROLES
from app.repositories import audit_log_repo, member_repo, user_repo
from app.schemas.dashboard import AdminSummary
from app.utils.time import created_at_filter, today_wib


async def admin_summary(db: AsyncDatabase) -> AdminSummary:
    by_role = await user_repo.count_active_by_role(db)
    today = today_wib()
    return AdminSummary(
        active_users=sum(by_role.values()),
        # Role tanpa user tetap dikirim dengan 0 supaya kartu di frontend tidak hilang.
        users_by_role={str(r): by_role.get(str(r), 0) for r in STAFF_ROLES},
        active_members=await member_repo.count_active(db),
        audit_logs_today=await audit_log_repo.count(db, created_at_filter(today, today)),
    )
