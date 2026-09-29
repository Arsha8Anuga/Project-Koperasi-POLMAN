"""Pembuat kode transaksi atomik: TRX-YYYYMMDD-NNNN dan RST-YYYYMMDD-NNNN."""

from __future__ import annotations

from datetime import datetime

from app.repositories import counter_repository
from app.utils.datetime_utils import to_wib, utcnow


async def next_code(db, prefix: str, session=None, at: datetime | None = None) -> str:
    """Buat kode transaksi berikutnya.

    Nomor urut reset setiap hari (hari menurut WIB) dan dibuat lewat collection counters,
    jangan pernah memakai count_documents() + 1. Fungsi ini juga dipakai BE-2 untuk kode RST.

    Bila dipanggil di dalam transaction, nomor urut ikut di-rollback saat transaksi gagal.
    Parameter at hanya dipakai skrip seed agar transaksi bisa dibuat di masa lalu.
    """
    moment = to_wib(at) if at else to_wib(utcnow())
    key = f"{prefix}-{moment.strftime('%Y%m%d')}"  # contoh: TRX-20260928
    seq = await counter_repository.increment(db, key, session)
    return f"{key}-{seq:04d}"  # contoh: TRX-20260928-0007
