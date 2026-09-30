"""Konfigurasi dari environment variable (sama gaya dengan backend)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from zoneinfo import ZoneInfo

WIB = ZoneInfo("Asia/Jakarta")

ROOT = Path(__file__).resolve().parents[1]  # folder ai-engine
# Urutan dicari: ai-engine/.env (khusus engine), lalu backend/.env (supaya DB-nya pasti sama dengan backend).
ENV_FILES = (ROOT / ".env", ROOT.parent / "backend" / ".env")
ENV_KEYS_PREFIX = ("MONGODB_", "AI_")


def _clean(value: str) -> str:
    """Buang spasi dan tanda kutip pembungkus: `"mongodb://..."` → `mongodb://...`."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        value = value[1:-1].strip()
    return value


def _env(name: str, default: str) -> str:
    value = os.environ.get(name)
    return default if value is None or not _clean(value) else _clean(value)


def load_env_files(files: tuple[Path, ...] = ENV_FILES) -> Path | None:
    """Isi MONGODB_* dan AI_* dari file .env pertama yang ada (untuk jalan di laptop).

    Environment variable yang sudah di-set TIDAK ditimpa (di Docker semuanya datang dari compose,
    dan file .env tidak ikut masuk image). Mengembalikan file yang dipakai, atau None.
    """
    for path in files:
        if not path.is_file():
            continue
        for raw in path.read_text(encoding="utf-8-sig").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.removeprefix("export ").split("=", 1)
            key = key.strip()
            if key.startswith(ENV_KEYS_PREFIX) and key not in os.environ:
                os.environ[key] = _clean(value)
        return path
    return None


def uri_problem(uri: str) -> str | None:
    """Pesan singkat kalau URI jelas salah. Isi URI tidak ikut ditampilkan (mengandung password)."""
    if uri.startswith(("mongodb://", "mongodb+srv://")):
        return None
    if uri.startswith("<") or "isi" in uri.lower():
        return "MONGODB_URI masih berisi teks contoh, belum diganti URI asli"
    return f"MONGODB_URI harus diawali mongodb:// atau mongodb+srv:// (sekarang diawali {uri[:3]!r}…)"


@dataclass(frozen=True)
class AssociationParams:
    history_days: int = 90  # transaksi yang dianalisis
    min_support: float = 0.01  # itemset muncul di >= 1% transaksi
    min_confidence: float = 0.2
    min_lift: float = 1.1  # > 1 = lebih sering bersama daripada kebetulan
    max_len: int = 3  # itemset terbesar (antecedent 2 + consequent 1)
    max_rules: int = 300


@dataclass(frozen=True)
class ForecastParams:
    history_days: int = 84  # 12 minggu
    horizon_days: int = 14
    lead_time_days: int = 3  # waktu tunggu barang datang dari supplier
    review_days: int = 7  # jarak antar restock rutin
    service_level: float = 0.95  # peluang stok tidak habis selama lead time
    backtest_days: int = 7
    history_output_days: int = 28  # data aktual yang ikut dikirim untuk chart


@dataclass(frozen=True)
class Settings:
    mongodb_uri: str = field(
        default_factory=lambda: _env("MONGODB_URI", "mongodb://localhost:27017/?directConnection=true")
    )
    mongodb_db: str = field(default_factory=lambda: _env("MONGODB_DB", "koperasi_dev"))
    interval_minutes: int = field(default_factory=lambda: int(_env("AI_INTERVAL_MINUTES", "15")))
    poll_seconds: int = field(default_factory=lambda: int(_env("AI_POLL_SECONDS", "10")))
    association: AssociationParams = field(
        default_factory=lambda: AssociationParams(
            history_days=int(_env("AI_ASSOC_HISTORY_DAYS", "90")),
            min_support=float(_env("AI_MIN_SUPPORT", "0.01")),
            min_confidence=float(_env("AI_MIN_CONFIDENCE", "0.2")),
            min_lift=float(_env("AI_MIN_LIFT", "1.1")),
        )
    )
    forecast: ForecastParams = field(
        default_factory=lambda: ForecastParams(
            lead_time_days=int(_env("AI_LEAD_TIME_DAYS", "3")),
            review_days=int(_env("AI_REVIEW_DAYS", "7")),
            service_level=float(_env("AI_SERVICE_LEVEL", "0.95")),
        )
    )
