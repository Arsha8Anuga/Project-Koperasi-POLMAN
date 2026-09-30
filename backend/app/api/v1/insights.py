"""Hasil AI engine (dibaca) + antrean hitung ulang (khusus ADMIN).

| Endpoint | Role |
|---|---|
| GET  /insights/frequently-bought?productIds=a,b | KASIR, OWNER, LOGISTIK |
| GET  /insights/association-rules               | OWNER, ADMIN |
| GET  /insights/forecast                        | LOGISTIK, OWNER |
| GET  /insights/forecast/{productId}            | LOGISTIK, OWNER |
| GET  /insights/status                          | ADMIN, OWNER |
| POST /insights/jobs                            | ADMIN |
"""

from fastapi import APIRouter, Depends, Query
from pymongo.asynchronous.database import AsyncDatabase

from app.api.deps import CurrentUser, get_db, require_roles
from app.core.enums import Role
from app.schemas.common import ERROR_RESPONSES, ApiResponse
from app.schemas.insight import (
    AiJobOut,
    AiStatusOut,
    AssociationRulesOut,
    ForecastDetailOut,
    ForecastListOut,
    SuggestionsOut,
)
from app.services import insight_service
from app.utils.response import ok

router = APIRouter(prefix="/insights", tags=["insights (AI)"], responses=ERROR_RESPONSES)


@router.get("/frequently-bought", response_model=ApiResponse[SuggestionsOut])
async def frequently_bought(
    product_ids: str = Query(
        "", alias="productIds", max_length=2000, description="ID produk di keranjang, dipisah koma"
    ),
    limit: int = Query(3, ge=1, le=10),
    _: CurrentUser = Depends(require_roles(Role.KASIR, Role.OWNER, Role.LOGISTIK)),
    db: AsyncDatabase = Depends(get_db),
):
    ids = [p.strip() for p in product_ids.split(",") if p.strip()][:50]
    return ok(await insight_service.frequently_bought(db, ids, limit))


@router.get("/association-rules", response_model=ApiResponse[AssociationRulesOut])
async def association_rules(
    limit: int = Query(20, ge=1, le=200),
    min_lift: float = Query(1.0, alias="minLift", ge=0),
    _: CurrentUser = Depends(require_roles(Role.OWNER, Role.ADMIN)),
    db: AsyncDatabase = Depends(get_db),
):
    return ok(await insight_service.association_rules(db, limit, min_lift))


@router.get("/forecast", response_model=ApiResponse[ForecastListOut])
async def forecast_list(
    _: CurrentUser = Depends(require_roles(Role.LOGISTIK, Role.OWNER)),
    db: AsyncDatabase = Depends(get_db),
):
    return ok(await insight_service.forecast_list(db))


@router.get("/forecast/{product_id}", response_model=ApiResponse[ForecastDetailOut])
async def forecast_detail(
    product_id: str,
    _: CurrentUser = Depends(require_roles(Role.LOGISTIK, Role.OWNER)),
    db: AsyncDatabase = Depends(get_db),
):
    return ok(await insight_service.forecast_detail(db, product_id))


@router.get("/status", response_model=ApiResponse[AiStatusOut])
async def status(
    _: CurrentUser = Depends(require_roles(Role.ADMIN, Role.OWNER)),
    db: AsyncDatabase = Depends(get_db),
):
    return ok(await insight_service.status(db))


@router.post("/jobs", status_code=201, response_model=ApiResponse[AiJobOut])
async def request_job(
    user: CurrentUser = Depends(require_roles(Role.ADMIN)),
    db: AsyncDatabase = Depends(get_db),
):
    return ok(await insight_service.request_job(db, user), "Perhitungan ulang dimasukkan ke antrean")
