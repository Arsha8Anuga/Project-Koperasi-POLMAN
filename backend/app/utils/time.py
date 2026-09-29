"""Waktu. Aturan: DISIMPAN selalu UTC; ditafsirkan (filter from/to, "hari ini", kode transaksi) dalam WIB."""

from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

WIB = ZoneInfo("Asia/Jakarta")


def utcnow() -> datetime:
    """Waktu sekarang (UTC, aware), dibulatkan ke milidetik seperti presisi MongoDB."""
    now = datetime.now(UTC)
    return now.replace(microsecond=now.microsecond // 1000 * 1000)


def now_wib() -> datetime:
    return datetime.now(WIB)


def today_wib() -> date:
    return now_wib().date()


def wib_day_start_utc(d: date) -> datetime:
    """00:00 WIB tanggal `d`, dalam UTC."""
    return datetime.combine(d, time.min, tzinfo=WIB).astimezone(UTC)


def wib_range_to_utc(date_from: date | None, date_to: date | None) -> tuple[datetime | None, datetime | None]:
    """Filter `from`/`to` (inklusif, WIB) → rentang UTC `[start, end)` (dokumen 05 §5.4)."""
    start = wib_day_start_utc(date_from) if date_from else None
    end = wib_day_start_utc(date_to + timedelta(days=1)) if date_to else None
    return start, end


def created_at_filter(date_from: date | None, date_to: date | None, field: str = "createdAt") -> dict:
    """Potongan filter MongoDB untuk rentang tanggal WIB. Kosong jika tidak ada filter."""
    start, end = wib_range_to_utc(date_from, date_to)
    cond: dict = {}
    if start:
        cond["$gte"] = start
    if end:
        cond["$lt"] = end
    return {field: cond} if cond else {}
