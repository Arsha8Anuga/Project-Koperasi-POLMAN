"""Satu-satunya exception bisnis. Di-raise dari service/deps, diubah ke format error standar
oleh `app.middlewares.error_handler` (dokumen 04 §2–3)."""

from typing import Any


class AppError(Exception):
    def __init__(
        self,
        status: int,
        code: str,
        message: str,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.details = details or []


# Pintasan untuk error yang sering dipakai. Pesan boleh diganti sesuai konteks.
def not_found(message: str = "Data tidak ditemukan") -> AppError:
    return AppError(404, "NOT_FOUND", message)


def bad_request(message: str, details: list[dict[str, Any]] | None = None) -> AppError:
    return AppError(400, "BAD_REQUEST", message, details)


def forbidden(message: str = "Anda tidak memiliki akses ke fitur ini") -> AppError:
    return AppError(403, "FORBIDDEN", message)


def duplicate(message: str, field: str | None = None) -> AppError:
    return AppError(409, "DUPLICATE", message, [{"field": field}] if field else None)
