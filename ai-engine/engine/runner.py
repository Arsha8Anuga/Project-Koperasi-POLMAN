"""Satu kali perhitungan: baca data → jalankan model → tulis ke collection `insights`."""

from __future__ import annotations

import logging
import math
import time
from dataclasses import asdict
from datetime import UTC, datetime, timedelta
from typing import Any

import numpy as np

from engine import __version__
from engine.association import apriori
from engine.config import WIB, Settings
from engine.data import daily_sales, load_baskets, load_products, stockout_days
from engine.forecast import choose_and_forecast, days_until_stockout, restock_advice

log = logging.getLogger("engine.runner")

BAND_Z = 1.28  # rentang prediksi ±80%


def _ref(pid: str, products: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    p = products.get(pid)
    if p is None:
        return None
    return {"productId": p["_id"], "sku": p["sku"], "name": p["name"]}


def compute_association(db, settings: Settings, now: datetime) -> dict[str, Any]:
    params = settings.association
    started = time.perf_counter()
    since = now - timedelta(days=params.history_days)
    baskets = load_baskets(db, since)
    result = apriori(
        baskets, params.min_support, params.min_confidence, params.min_lift, params.max_len, params.max_rules
    )
    products = load_products(db, active_only=False)

    rules = []
    for r in result.rules:
        antecedent = [_ref(pid, products) for pid in r.antecedent]
        consequent = _ref(r.consequent, products)
        if consequent is None or any(a is None for a in antecedent):
            continue  # produk sudah dihapus dari katalog
        rules.append(
            {
                "antecedent": antecedent,
                "consequent": [consequent],
                "support": r.support,
                "confidence": r.confidence,
                "lift": r.lift,
                "count": r.count,
            }
        )

    return {
        "kind": "association_rules",
        "algorithm": "apriori",
        "params": asdict(params),
        "stats": {
            "transactions": result.transactions,
            "items": result.items,
            "frequentItemsets": result.frequent_itemsets,
            "rules": len(rules),
            "from": since,
            "to": now,
            "durationMs": round((time.perf_counter() - started) * 1000),
        },
        "rules": rules,
    }


def compute_forecast(db, settings: Settings, now: datetime) -> dict[str, Any]:
    params = settings.forecast
    started = time.perf_counter()
    today = now.astimezone(WIB).date()
    last_day = today - timedelta(days=1)  # hari ini belum selesai: tidak dipakai melatih
    first_day = last_day - timedelta(days=params.history_days - 1)

    sales = daily_sales(db, first_day, last_day)
    censored = stockout_days(db, first_day, last_day)
    products = load_products(db, active_only=True)
    zeros = np.zeros(params.history_days)

    out = []
    model_count: dict[str, int] = {}
    for pid, p in products.items():
        raw = sales.get(pid, zeros).astype(float)
        cens = sorted(i for i in censored.get(pid, set()) if 0 <= i < len(raw))
        train = raw.copy()
        train[cens] = np.nan
        choice = choose_and_forecast(train, params.horizon_days, params.backtest_days)
        model_count[choice.model] = model_count.get(choice.model, 0) + 1

        stock = int(p.get("stock", 0))
        days_left = days_until_stockout(stock, choice.forecast)
        advice = restock_advice(
            stock, choice.forecast, choice.sigma, params.lead_time_days, params.review_days, params.service_level
        )
        forecast_points = []
        for h, qty in enumerate(choice.forecast, start=1):
            band = BAND_Z * choice.sigma * math.sqrt(h)
            forecast_points.append(
                {
                    "date": (today + timedelta(days=h - 1)).isoformat(),
                    "qty": round(float(qty), 2),
                    "lower": round(max(0.0, float(qty) - band), 2),
                    "upper": round(float(qty) + band, 2),
                }
            )
        history_start = max(0, len(raw) - params.history_output_days)
        history = [
            {"date": (first_day + timedelta(days=i)).isoformat(), "qty": float(raw[i])}
            for i in range(history_start, len(raw))
        ]
        stockout_date = None
        if days_left is not None and days_left <= params.horizon_days:
            stockout_date = (today + timedelta(days=int(math.floor(days_left)))).isoformat()

        out.append(
            {
                "productId": p["_id"],
                "sku": p["sku"],
                "name": p["name"],
                "unit": p.get("unit", ""),
                "stock": stock,
                "avgDaily": round(float(np.mean(choice.forecast)), 2),
                "model": choice.model,
                "modelParams": choice.params,
                "wape": choice.wape,
                "baselineWape": choice.baseline_wape,
                "daysUntilStockout": days_left,
                "stockoutDate": stockout_date,
                "suggestedQty": advice.suggested_qty,
                "reorderNeeded": advice.reorder_needed,
                "reorderPoint": advice.reorder_point,
                "safetyStock": advice.safety_stock,
                "excludedStockoutDays": len(cens),
                "history": history,
                "forecast": forecast_points,
            }
        )

    wapes = [x["wape"] for x in out if x["wape"] is not None]
    return {
        "kind": "forecast",
        "params": asdict(params),
        "stats": {
            "products": len(out),
            "models": model_count,
            "avgWape": round(float(np.mean(wapes)), 4) if wapes else None,
            "reorderNeeded": sum(1 for x in out if x["reorderNeeded"]),
            "from": first_day.isoformat(),
            "to": last_day.isoformat(),
            "durationMs": round((time.perf_counter() - started) * 1000),
        },
        "products": out,
    }


COMPUTE = {"association_rules": compute_association, "forecast": compute_forecast}


def run(db, settings: Settings, kinds: list[str], job_id=None) -> dict[str, Any]:
    """Hitung jenis analisis yang diminta dan timpa dokumen `insights`-nya. Mengembalikan ringkasan."""
    now = datetime.now(UTC)
    summary: dict[str, Any] = {}
    for kind in kinds:
        doc = COMPUTE[kind](db, settings, now)
        doc.update({"generatedAt": datetime.now(UTC), "jobId": job_id, "engineVersion": __version__})
        db["insights"].replace_one({"_id": kind}, {"_id": kind, **doc}, upsert=True)
        summary[kind] = doc["stats"]
        log.info("%s selesai: %s", kind, {k: v for k, v in doc["stats"].items() if k not in ("from", "to")})
    return summary
