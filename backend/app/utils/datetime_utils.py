"""Fungsi bantu waktu.

Aturan proyek (BR-11):
- Semua waktu disimpan di database dalam UTC.
- Filter tanggal dari frontend (YYYY-MM-DD) ditafsirkan dalam zona Asia/Jakarta (WIB).
- Agregasi laporan mengelompokkan data berdasarkan hari, minggu, bulan, atau tahun WIB.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.core.errors import AppError

TZ_NAME = "Asia/Jakarta"

try:
    WIB = ZoneInfo(TZ_NAME)
except ZoneInfoNotFoundError:
    # Windows tidak punya database zona waktu bawaan. Jalankan "pip install tzdata".
    # Indonesia bagian barat tidak memakai DST, jadi offset tetap +07:00 sudah tepat.
    WIB = timezone(timedelta(hours=7), name="WIB")


def utcnow() -> datetime:
    """Waktu sekarang dalam UTC (timezone-aware)."""
    return datetime.now(timezone.utc)


def ensure_utc(value: datetime) -> datetime:
    """Ubah datetime menjadi UTC aware.

    PyMongo secara bawaan mengembalikan datetime tanpa zona (naive) yang isinya UTC.
    Jadi datetime naive dianggap UTC.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def to_wib(value: datetime) -> datetime:
    """Ubah datetime menjadi WIB."""
    return ensure_utc(value).astimezone(WIB)


def now_wib() -> datetime:
    return utcnow().astimezone(WIB)


def today_wib() -> date:
    return now_wib().date()


def wib_day_start_utc(day: date) -> datetime:
    """Awal hari (00:00 WIB) dari tanggal tertentu, dinyatakan dalam UTC."""
    return datetime.combine(day, time.min, tzinfo=WIB).astimezone(timezone.utc)


def wib_range_to_utc(from_date: date, to_date: date) -> tuple[datetime, datetime]:
    """Ubah rentang tanggal WIB (inklusif) menjadi rentang UTC [start, end).

    start = from 00:00 WIB
    end   = (to + 1 hari) 00:00 WIB, batas atas eksklusif.
    """
    start = wib_day_start_utc(from_date)
    end = wib_day_start_utc(to_date + timedelta(days=1))
    return start, end


def date_bounds(
    from_date: date | None, to_date: date | None
) -> tuple[datetime | None, datetime | None]:
    """Sama seperti wib_range_to_utc, tetapi salah satu ujung boleh kosong."""
    start = wib_day_start_utc(from_date) if from_date else None
    end = wib_day_start_utc(to_date + timedelta(days=1)) if to_date else None
    return start, end


def validate_date_order(from_date: date | None, to_date: date | None) -> None:
    """Pastikan tanggal awal tidak melebihi tanggal akhir."""
    if from_date and to_date and from_date > to_date:
        raise AppError(
            422,
            "VALIDATION_ERROR",
            "Tanggal awal tidak boleh lebih besar dari tanggal akhir",
            [{"field": "from", "message": "Harus lebih kecil atau sama dengan tanggal akhir (to)"}],
        )
