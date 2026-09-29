from datetime import date

from fastapi import APIRouter, Depends, Query
from pymongo.asynchronous.database import AsyncDatabase

from app.api.deps import CurrentUser, get_db, require_roles
from app.core.enums import AuditAction, AuditModule, Role
from app.schemas.audit_log import AuditLogOut
from app.schemas.common import ERROR_RESPONSES, PaginatedResponse
from app.services import audit_service
from app.utils.pagination import PageParams
from app.utils.response import paginated

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"], responses=ERROR_RESPONSES)


@router.get("", response_model=PaginatedResponse[AuditLogOut])
async def list_audit_logs(
    page: PageParams = Depends(),
    user_id: str | None = Query(None, alias="userId"),
    module: AuditModule | None = None,
    action: AuditAction | None = None,
    date_from: date | None = Query(None, alias="from", description="YYYY-MM-DD, WIB, inklusif"),
    date_to: date | None = Query(None, alias="to", description="YYYY-MM-DD, WIB, inklusif"),
    _: CurrentUser = Depends(require_roles(Role.ADMIN)),
    db: AsyncDatabase = Depends(get_db),
):
    items, total = await audit_service.list_logs(db, page, user_id, module, action, date_from, date_to)
    return paginated(items, page, total)
