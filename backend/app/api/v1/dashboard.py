from fastapi import APIRouter, Depends
from pymongo.asynchronous.database import AsyncDatabase

from app.api.deps import CurrentUser, get_db, require_roles
from app.core.enums import Role
from app.schemas.common import ERROR_RESPONSES, ApiResponse
from app.schemas.dashboard import DashboardSummary
from app.services import dashboard
from app.utils.response import ok

router = APIRouter(prefix="/dashboard", tags=["dashboard"], responses=ERROR_RESPONSES)


@router.get("/summary", response_model=ApiResponse[DashboardSummary])
async def summary(
    user: CurrentUser = Depends(require_roles(Role.OWNER, Role.LOGISTIK, Role.ADMIN)),
    db: AsyncDatabase = Depends(get_db),
):
    return ok(await dashboard.get_summary(db, user))
