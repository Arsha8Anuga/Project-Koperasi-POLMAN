"""Kontrak data AI engine ↔ backend (engine menulis, backend hanya membaca + membuat job).

Collection yang dipakai (nama field camelCase, sama dengan konvensi proyek):

``insights``  — satu dokumen per jenis analisis, ditimpa setiap engine selesai:
    {_id: "association_rules" | "forecast", kind, generatedAt, jobId, engineVersion,
     params: {...}, stats: {...}, rules: [...] | products: [...]}

``ai_jobs``   — antrean & riwayat perhitungan:
    {_id, status: PENDING|RUNNING|DONE|FAILED, trigger: MANUAL|SCHEDULE|SEED,
     kinds: [...], requestedBy: {id,name,role}|null, requestedAt, startedAt, finishedAt,
     error, summary: {...}}

``ai_engine_status`` — denyut engine: {_id: "engine", lastSeenAt, version, intervalMinutes, host}

Bentuk lengkap tiap field ada di ai-engine/CONTRACT.md. Mengubah bentuk = mengubah engine juga.
"""

from datetime import date, datetime

from app.core.enums import InsightKind, JobStatus, JobTrigger, Role
from app.schemas.common import CamelModel, ObjectIdStr, UtcDatetime


class InsightProductRef(CamelModel):
    product_id: ObjectIdStr
    sku: str
    name: str


# ---------- association rules ----------
class AssociationRule(CamelModel):
    antecedent: list[InsightProductRef]
    consequent: list[InsightProductRef]
    support: float
    confidence: float
    lift: float
    count: int


class InsightMeta(CamelModel):
    generated_at: UtcDatetime
    params: dict
    stats: dict


class AssociationRulesOut(CamelModel):
    meta: InsightMeta | None
    rules: list[AssociationRule]


class SuggestionProduct(CamelModel):
    id: ObjectIdStr
    sku: str
    name: str
    unit: str
    selling_price: int
    stock: int
    image_url: str | None = None


class Suggestion(CamelModel):
    product: SuggestionProduct
    because: list[str]
    confidence: float
    lift: float


class SuggestionsOut(CamelModel):
    generated_at: UtcDatetime | None
    items: list[Suggestion]


# ---------- forecast ----------
class DailyPoint(CamelModel):
    date: date
    qty: float
    lower: float | None = None
    upper: float | None = None


class ForecastSummary(CamelModel):
    product_id: ObjectIdStr
    sku: str
    name: str
    unit: str
    stock: int
    avg_daily: float
    model: str
    wape: float | None = None
    baseline_wape: float | None = None
    days_until_stockout: float | None = None
    stockout_date: date | None = None
    suggested_qty: int
    reorder_needed: bool
    reorder_point: float | None = None


class ForecastDetail(ForecastSummary):
    safety_stock: int
    model_params: dict | None = None
    history: list[DailyPoint]
    forecast: list[DailyPoint]
    excluded_stockout_days: int = 0


class ForecastListOut(CamelModel):
    meta: InsightMeta | None
    products: list[ForecastSummary]


class ForecastDetailOut(CamelModel):
    meta: InsightMeta | None
    product: ForecastDetail


# ---------- job & status ----------
class JobActor(CamelModel):
    id: str
    name: str
    role: Role


class AiJobOut(CamelModel):
    id: ObjectIdStr
    status: JobStatus
    trigger: JobTrigger
    kinds: list[InsightKind]
    requested_by: JobActor | None = None
    requested_at: UtcDatetime
    started_at: UtcDatetime | None = None
    finished_at: UtcDatetime | None = None
    error: str | None = None
    summary: dict | None = None


class EngineStatus(CamelModel):
    online: bool
    last_seen_at: UtcDatetime | None = None
    version: str | None = None
    interval_minutes: int | None = None


class InsightFreshness(CamelModel):
    kind: InsightKind
    generated_at: datetime | None
    stats: dict | None = None


class AiStatusOut(CamelModel):
    engine: EngineStatus
    active_job: AiJobOut | None
    insights: list[InsightFreshness]
    recent_jobs: list[AiJobOut]
