"""Membaca hasil AI engine & mengantrekan perhitungan ulang.

Backend TIDAK menjalankan model. Engine (container ai-engine) membaca transaksi, menghitung,
lalu menulis ke collection `insights`. Kalau engine mati, endpoint di sini tetap jalan dengan
hasil terakhir — checkout kasir tidak pernah bergantung pada engine.
"""

from datetime import timedelta
from typing import Any

from pymongo.asynchronous.database import AsyncDatabase

from app.core.enums import AuditAction, AuditModule, InsightKind, JobStatus, JobTrigger
from app.core.errors import AppError, not_found
from app.repositories import insight_repo, product_repo
from app.schemas.auth import CurrentUser
from app.schemas.insight import (
    AiJobOut,
    AiStatusOut,
    AssociationRule,
    AssociationRulesOut,
    EngineStatus,
    ForecastDetail,
    ForecastDetailOut,
    ForecastListOut,
    ForecastSummary,
    InsightFreshness,
    InsightMeta,
    Suggestion,
    SuggestionProduct,
    SuggestionsOut,
)
from app.services import audit_service as audit
from app.utils.objectid import try_object_id
from app.utils.time import ensure_utc, utcnow

STALE_RUNNING = timedelta(minutes=30)
ENGINE_OFFLINE_AFTER = timedelta(minutes=3)
ALL_KINDS = [InsightKind.ASSOCIATION_RULES, InsightKind.FORECAST]


def _meta(doc: dict[str, Any] | None) -> InsightMeta | None:
    if not doc:
        return None
    return InsightMeta(
        generated_at=doc["generatedAt"], params=doc.get("params") or {}, stats=doc.get("stats") or {}
    )


# ---------------------------------------------------------------------------
# Association rules
# ---------------------------------------------------------------------------


async def frequently_bought(db: AsyncDatabase, product_ids: list[str], limit: int = 3) -> SuggestionsOut:
    """Saran untuk keranjang kasir: aturan yang semua 'antecedent'-nya ada di keranjang dan
    'consequent'-nya belum. Produk nonaktif / stok habis tidak disarankan."""
    doc = await insight_repo.get_insight(db, InsightKind.ASSOCIATION_RULES)
    cart = {pid for pid in product_ids if pid}
    if not doc or not cart:
        return SuggestionsOut(generated_at=doc["generatedAt"] if doc else None, items=[])

    best: dict[str, tuple[float, float, list[str]]] = {}  # productId -> (confidence, lift, because)
    for rule in doc.get("rules", []):
        ante = {str(p["productId"]) for p in rule["antecedent"]}
        if not ante or not ante <= cart:
            continue
        for c in rule["consequent"]:
            cid = str(c["productId"])
            if cid in cart:
                continue
            score = (rule["confidence"], rule["lift"], [p["name"] for p in rule["antecedent"]])
            if cid not in best or score[:2] > best[cid][:2]:
                best[cid] = score

    ranked = sorted(best.items(), key=lambda kv: (kv[1][0], kv[1][1]), reverse=True)
    ids = [oid for oid in (try_object_id(pid) for pid, _ in ranked) if oid is not None]
    products = {str(p["_id"]): p for p in await product_repo.find_by_ids(db, ids)}

    items: list[Suggestion] = []
    for pid, (confidence, lift, because) in ranked:
        p = products.get(pid)
        if not p or not p.get("isActive") or int(p.get("stock", 0)) <= 0:
            continue
        items.append(
            Suggestion(
                product=SuggestionProduct(
                    id=p["_id"],
                    sku=p["sku"],
                    name=p["name"],
                    unit=p["unit"],
                    selling_price=p["sellingPrice"],
                    stock=p["stock"],
                ),
                because=because,
                confidence=confidence,
                lift=lift,
            )
        )
        if len(items) >= limit:
            break
    return SuggestionsOut(generated_at=doc["generatedAt"], items=items)


async def association_rules(db: AsyncDatabase, limit: int, min_lift: float) -> AssociationRulesOut:
    doc = await insight_repo.get_insight(db, InsightKind.ASSOCIATION_RULES)
    if not doc:
        return AssociationRulesOut(meta=None, rules=[])
    rules = [r for r in doc.get("rules", []) if r["lift"] >= min_lift]
    rules.sort(key=lambda r: (r["lift"] * r["confidence"], r["count"]), reverse=True)
    return AssociationRulesOut(
        meta=_meta(doc), rules=[AssociationRule.model_validate(r) for r in rules[:limit]]
    )


# ---------------------------------------------------------------------------
# Forecast
# ---------------------------------------------------------------------------


async def forecast_list(db: AsyncDatabase) -> ForecastListOut:
    doc = await insight_repo.get_insight(db, InsightKind.FORECAST)
    if not doc:
        return ForecastListOut(meta=None, products=[])
    products = [ForecastSummary.model_validate(p) for p in doc.get("products", [])]
    # paling mendesak dulu; produk yang tidak diperkirakan habis di akhir
    products.sort(key=lambda p: (p.days_until_stockout is None, p.days_until_stockout or 0, p.name))
    return ForecastListOut(meta=_meta(doc), products=products)


async def forecast_detail(db: AsyncDatabase, product_id: str) -> ForecastDetailOut:
    doc = await insight_repo.get_insight(db, InsightKind.FORECAST)
    for p in (doc or {}).get("products", []):
        if str(p["productId"]) == product_id:
            return ForecastDetailOut(meta=_meta(doc), product=ForecastDetail.model_validate(p))
    raise not_found("Prediksi untuk produk ini belum tersedia")


# ---------------------------------------------------------------------------
# Status & job
# ---------------------------------------------------------------------------


def _job(doc: dict[str, Any]) -> AiJobOut:
    return AiJobOut.model_validate({**doc, "id": doc["_id"]})


async def status(db: AsyncDatabase) -> AiStatusOut:
    now = utcnow()
    await insight_repo.fail_stale_running(db, now - STALE_RUNNING, now)

    eng = await insight_repo.engine_status(db)
    last_seen = ensure_utc(eng["lastSeenAt"]) if eng and eng.get("lastSeenAt") else None
    engine = EngineStatus(
        online=bool(last_seen and now - last_seen <= ENGINE_OFFLINE_AFTER),
        last_seen_at=last_seen,
        version=(eng or {}).get("version"),
        interval_minutes=(eng or {}).get("intervalMinutes"),
    )

    freshness = []
    for kind in ALL_KINDS:
        meta = await insight_repo.insight_meta(db, kind)
        freshness.append(
            InsightFreshness(
                kind=kind, generated_at=meta["generatedAt"] if meta else None, stats=(meta or {}).get("stats")
            )
        )

    active = await insight_repo.find_active_job(db)
    recent = await insight_repo.recent_jobs(db, 10)
    return AiStatusOut(
        engine=engine,
        active_job=_job(active) if active else None,
        insights=freshness,
        recent_jobs=[_job(j) for j in recent],
    )


async def request_job(
    db: AsyncDatabase, actor: CurrentUser, trigger: JobTrigger = JobTrigger.MANUAL
) -> AiJobOut:
    now = utcnow()
    await insight_repo.fail_stale_running(db, now - STALE_RUNNING, now)
    if await insight_repo.find_active_job(db):
        raise AppError(409, "JOB_IN_PROGRESS", "Perhitungan ulang sedang berjalan atau mengantre")

    job = await insight_repo.insert_job(
        db,
        {
            "status": JobStatus.PENDING.value,
            "trigger": trigger.value,
            "kinds": [k.value for k in ALL_KINDS],
            "requestedBy": {"id": actor.id, "name": actor.name, "role": actor.role.value},
            "requestedAt": now,
            "startedAt": None,
            "finishedAt": None,
            "error": None,
            "summary": None,
        },
    )
    await audit.log(
        db,
        actor,
        AuditAction.RECOMPUTE,
        AuditModule.AI,
        job["_id"],
        "Meminta AI engine menghitung ulang analisis",
    )
    return _job(job)
