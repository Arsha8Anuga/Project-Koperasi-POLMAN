"""Forecasting penjualan harian per produk + saran restock.

Model utama: Holt-Winters aditif dengan tren teredam (damped) dan musiman mingguan (7 hari):

    level_t    = α (y_t − s_{t−7}) + (1 − α)(level_{t−1} + φ·trend_{t−1})
    trend_t    = β (level_t − level_{t−1}) + (1 − β) φ·trend_{t−1}
    season_t   = γ (y_t − level_t) + (1 − γ) s_{t−7}
    ŷ_{t+h}    = level_t + (φ + φ² + … + φ^h)·trend_t + s_{t+h−7}

α, β, γ dipilih dengan grid search yang meminimalkan galat prediksi 1-langkah (SSE).

Aturan pemilihan model per produk:
- Data < 21 hari atau > 60% hari tanpa penjualan → Holt-Winters tidak stabil:
  pakai Croston (khusus permintaan jarang) atau rata-rata bergerak.
- Backtest 7 hari terakhir (28 hari untuk Croston): kalau model tidak lebih baik dari baseline
  "rata-rata 7 hari", pakai baseline. Akurasi dilaporkan sebagai WAPE = Σ|aktual−prediksi| / Σ aktual.

Hari ketika stok habis (penjualan 0 karena barang tidak ada, bukan karena tidak laku)
dikeluarkan dari data latih (NaN) dan diisi rata-rata hari yang sama di minggu lain.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import product as grid

import numpy as np

SEASON = 7
PHI = 0.9  # redaman tren: tren tidak diteruskan lurus selamanya
ALPHAS = (0.1, 0.2, 0.3, 0.5, 0.7)
BETAS = (0.01, 0.05, 0.1, 0.2)
GAMMAS = (0.05, 0.1, 0.2, 0.3)


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------


def fill_censored(y: np.ndarray) -> np.ndarray:
    """NaN (hari stok habis) diisi rata-rata hari yang sama dalam minggu; kalau tidak ada, rata-rata umum."""
    y = y.astype(float).copy()
    if not np.isnan(y).any():
        return y
    overall = np.nanmean(y) if np.isfinite(np.nanmean(y)) else 0.0
    for d in range(SEASON):
        idx = np.arange(d, len(y), SEASON)
        vals = y[idx]
        mean = np.nanmean(vals) if np.isfinite(vals).any() else overall
        vals[np.isnan(vals)] = mean
        y[idx] = vals
    return y


def _holt_winters_pass(y: np.ndarray, alpha: float, beta: float, gamma: float):
    n = len(y)
    level = y[:SEASON].mean()
    trend = (y[SEASON : 2 * SEASON].mean() - y[:SEASON].mean()) / SEASON if n >= 2 * SEASON else 0.0
    season = list(y[:SEASON] - level)
    errors = []
    for t in range(SEASON, n):
        s = season[t - SEASON]
        pred = level + PHI * trend + s
        errors.append(y[t] - pred)
        prev_level = level
        level = alpha * (y[t] - s) + (1 - alpha) * (prev_level + PHI * trend)
        trend = beta * (level - prev_level) + (1 - beta) * PHI * trend
        season.append(gamma * (y[t] - level) + (1 - gamma) * s)
    return level, trend, season, np.array(errors)


def holt_winters(y: np.ndarray, horizon: int) -> tuple[np.ndarray, float, dict]:
    """Fit + prediksi. Mengembalikan (prediksi, simpangan baku galat 1-langkah, parameter)."""
    best = None
    for alpha, beta, gamma in grid(ALPHAS, BETAS, GAMMAS):
        level, trend, season, err = _holt_winters_pass(y, alpha, beta, gamma)
        sse = float(np.sum(err**2))
        if best is None or sse < best[0]:
            best = (sse, alpha, beta, gamma, level, trend, season, err)
    assert best is not None
    _sse, alpha, beta, gamma, level, trend, season, err = best
    n = len(y)
    out = []
    damp = 0.0
    for h in range(1, horizon + 1):
        damp += PHI**h
        s = season[n - SEASON + ((h - 1) % SEASON)]
        out.append(level + damp * trend + s)
    sigma = float(np.std(err, ddof=1)) if len(err) > 1 else float(np.std(y))
    return np.clip(np.array(out), 0, None), sigma, {"alpha": alpha, "beta": beta, "gamma": gamma, "phi": PHI}


def croston(y: np.ndarray, horizon: int, alpha: float = 0.1) -> tuple[np.ndarray, float]:
    """Croston: perkiraan ukuran permintaan saat terjadi ÷ jarak rata-rata antar permintaan."""
    nz = np.flatnonzero(y > 0)
    if len(nz) == 0:
        return np.zeros(horizon), 0.0
    gaps = np.diff(np.concatenate(([-1], nz)))
    # nilai awal = rata-rata keseluruhan, lalu dihaluskan mengikuti kejadian terbaru
    size = float(y[nz].mean())
    interval = float(gaps.mean())
    for i, gap in zip(nz, gaps, strict=True):
        size = alpha * y[i] + (1 - alpha) * size
        interval = alpha * gap + (1 - alpha) * interval
    rate = size / interval
    return np.full(horizon, rate), float(np.std(y))


def moving_average(y: np.ndarray, horizon: int, window: int = 7) -> tuple[np.ndarray, float]:
    recent = y[-window:] if len(y) >= window else y
    mean = float(recent.mean()) if len(recent) else 0.0
    return np.full(horizon, mean), float(np.std(y[-28:])) if len(y) else 0.0


def wape(actual: np.ndarray, predicted: np.ndarray) -> float | None:
    mask = ~np.isnan(actual)
    total = float(np.sum(actual[mask]))
    if total <= 0:
        return None
    return round(float(np.sum(np.abs(actual[mask] - predicted[mask]))) / total, 4)


# ---------------------------------------------------------------------------
# Pemilihan model + backtest
# ---------------------------------------------------------------------------


@dataclass
class ModelChoice:
    model: str  # holt_winters | moving_average | croston
    forecast: np.ndarray
    sigma: float
    wape: float | None
    baseline_wape: float | None
    params: dict


def _fit(kind: str, y: np.ndarray, horizon: int) -> tuple[np.ndarray, float, dict]:
    if kind == "holt_winters":
        return holt_winters(y, horizon)
    if kind == "croston":
        f, s = croston(y, horizon)
        return f, s, {}
    f, s = moving_average(y, horizon)
    return f, s, {"window": 7}


def choose_and_forecast(raw: np.ndarray, horizon: int, backtest_days: int = 7) -> ModelChoice:
    """raw: penjualan harian (NaN = hari stok habis), urut lama → baru, tanpa hari ini."""
    y = fill_censored(raw)
    observed = raw[~np.isnan(raw)]
    zero_ratio = float(np.mean(observed == 0)) if len(observed) else 1.0

    if len(y) < 3 * SEASON or zero_ratio > 0.6:
        candidate = "croston" if np.count_nonzero(observed) >= 4 else "moving_average"
    else:
        candidate = "holt_winters"

    model_wape = baseline_wape = None
    # permintaan jarang: 7 hari terlalu pendek untuk menilai (bisa saja 0 atau 1 penjualan) → uji 28 hari
    window = 4 * SEASON if candidate == "croston" else backtest_days
    if len(y) > window + 2 * SEASON:
        train, test = y[:-window], raw[-window:]
        pred, _s, _p = _fit(candidate, train, window)
        base, _s2 = moving_average(train, window)
        model_wape, baseline_wape = wape(test, pred), wape(test, base)
        # model yang tidak mengalahkan baseline sederhana tidak dipakai
        if candidate != "moving_average" and model_wape is not None and baseline_wape is not None:
            if model_wape > baseline_wape:
                candidate, model_wape = "moving_average", baseline_wape

    forecast, sigma, params = _fit(candidate, y, horizon)
    return ModelChoice(candidate, forecast, sigma, model_wape, baseline_wape, params)


# ---------------------------------------------------------------------------
# Dari prediksi ke keputusan restock
# ---------------------------------------------------------------------------

Z_BY_SERVICE = {0.8: 0.842, 0.85: 1.036, 0.9: 1.282, 0.95: 1.645, 0.975: 1.96, 0.99: 2.326}


def z_score(service_level: float) -> float:
    key = min(Z_BY_SERVICE, key=lambda k: abs(k - service_level))
    return Z_BY_SERVICE[key]


def days_until_stockout(stock: float, forecast: np.ndarray) -> float | None:
    """Hari (desimal) sampai stok habis menurut prediksi. None = tidak diperkirakan habis."""
    if stock <= 0:
        return 0.0
    cumulative = 0.0
    for i, f in enumerate(forecast):
        if f > 0 and cumulative + f >= stock:
            return round(i + (stock - cumulative) / f, 1)
        cumulative += f
    avg = float(np.mean(forecast)) if len(forecast) else 0.0
    if avg <= 0:
        return None
    # di luar horizon: perkiraan kasar dari rata-rata prediksi
    return round(min(len(forecast) + (stock - cumulative) / avg, 365.0), 1)


@dataclass
class RestockAdvice:
    safety_stock: int
    reorder_point: float
    suggested_qty: int
    reorder_needed: bool


def restock_advice(
    stock: int, forecast: np.ndarray, sigma: float, lead_time: int, review: int, service_level: float
) -> RestockAdvice:
    """Stok pengaman = z·σ·√(lead time); pesan cukup untuk (lead time + periode review) + stok pengaman."""
    safety = int(math.ceil(z_score(service_level) * sigma * math.sqrt(lead_time)))
    daily = list(forecast) + [float(np.mean(forecast)) if len(forecast) else 0.0] * (lead_time + review)
    demand_lead = float(sum(daily[:lead_time]))
    demand_cover = float(sum(daily[: lead_time + review]))
    reorder_point = demand_lead + safety
    suggested = max(0, int(math.ceil(demand_cover + safety - stock)))
    return RestockAdvice(safety, round(reorder_point, 1), suggested, stock <= reorder_point)
