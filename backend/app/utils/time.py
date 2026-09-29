"""Waktu. Aturan proyek (BR-11):

- DISIMPAN selalu UTC (datetime aware).
- Filter `from`/`to` (YYYY-MM-DD), "hari ini", kode transaksi, dan bucket laporan
  ditafsirkan dalam WIB (Asia/Jakarta).
"""

from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.core.errors import AppError

TZ_NAME = "Asia/Jakarta"
WIB = ZoneInfo(TZ_NAME)  # Windows: butuh paket `tzdata` (ada di requirements.txt)


def utcnow() -> datetime:
    """Waktu sekarang (UTC, aware), dibulatkan ke milidetik seperti presisi MongoDB."""
    now = datetime.now(UTC)
    return now.replace(microsecond=now.microsecond // 1000 * 1000)


def ensure_utc(value: datetime) -> datetime:
    """Datetime naive dianggap UTC; yang aware dikonversi ke UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def to_wib(value: datetime) -> datetime:
    return ensure_utc(value).astimezone(WIB)


def now_wib() -> datetime:
    return datetime.now(WIB)


def today_wib() -> date:
    return now_wib().date()


def wib_day_start_utc(d: date) -> datetime:
    """00:00 WIB tanggal `d`, dalam UTC."""
    return datetime.combine(d, time.min, tzinfo=WIB).astimezone(UTC)


def wib_month_start_utc(d: date) -> datetime:
    """Tanggal 1 bulan `d`, 00:00 WIB, dalam UTC."""
    return wib_day_start_utc(d.replace(day=1))


def wib_range_to_utc(date_from: date | None, date_to: date | None) -> tuple[datetime | None, datetime | None]:
    """Filter `from`/`to` (inklusif, WIB) → rentang UTC `[start, end)` (dokumen 05 §5.4).
    Salah satu ujung boleh kosong."""
    start = wib_day_start_utc(date_from) if date_from else None
    end = wib_day_start_utc(date_to + timedelta(days=1)) if date_to else None
    return start, end


def validate_date_order(date_from: date | None, date_to: date | None) -> None:
    if date_from and date_to and date_from > date_to:
        raise AppError(
            422,
            "VALIDATION_ERROR",
            "Tanggal awal tidak boleh lebih besar dari tanggal akhir",
            [{"field": "from", "message": "Harus lebih kecil atau sama dengan tanggal akhir"}],
        )


def created_at_filter(date_from: date | None, date_to: date | None, field: str = "createdAt") -> dict:
    """Potongan filter MongoDB untuk rentang tanggal WIB. Kosong jika tidak ada filter."""
    validate_date_order(date_from, date_to)
    start, end = wib_range_to_utc(date_from, date_to)
    cond: dict = {}
    if start:
        cond["$gte"] = start
    if end:
        cond["$lt"] = end
    return {field: cond} if cond else {}
