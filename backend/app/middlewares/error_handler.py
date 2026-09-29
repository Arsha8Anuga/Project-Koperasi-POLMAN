"""Semua error → format standar dokumen 04 §2:

{"success": false, "message": "...", "error": {"code": "...", "details": [...]}}
"""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pymongo.errors import DuplicateKeyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors import AppError

logger = logging.getLogger("app.errors")


def error_response(
    status: int, code: str, message: str, details: list[dict[str, Any]] | None = None
) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content=jsonable_encoder(
            {"success": False, "message": message, "error": {"code": code, "details": details or []}}
        ),
    )


# ---------- Validasi Pydantic → pesan Indonesia ----------

_MESSAGES: dict[str, str] = {
    "missing": "Wajib diisi",
    "string_type": "Harus berupa teks",
    "int_type": "Harus berupa bilangan bulat",
    "int_parsing": "Harus berupa bilangan bulat",
    "int_from_float": "Harus berupa bilangan bulat",
    "bool_type": "Harus berupa true/false",
    "bool_parsing": "Harus berupa true/false",
    "date_from_datetime_parsing": "Format tanggal harus YYYY-MM-DD",
    "date_parsing": "Format tanggal harus YYYY-MM-DD",
    "date_type": "Format tanggal harus YYYY-MM-DD",
    "enum": "Nilai tidak valid",
    "literal_error": "Nilai tidak valid",
    "string_pattern_mismatch": "Format tidak valid",
    "list_type": "Harus berupa array",
    "model_attributes_type": "Format data tidak valid",
    "dict_type": "Format data tidak valid",
    "json_invalid": "JSON tidak valid",
    "extra_forbidden": "Field tidak dikenal",
}


def _translate(err: dict[str, Any]) -> str:
    t, ctx = err.get("type", ""), err.get("ctx") or {}
    if t == "string_too_short":
        return "Wajib diisi" if ctx.get("min_length") == 1 else f"Minimal {ctx.get('min_length')} karakter"
    if t == "string_too_long":
        return f"Maksimal {ctx.get('max_length')} karakter"
    if t in ("greater_than_equal", "greater_than"):
        return f"Minimal {ctx.get('ge', ctx.get('gt'))}"
    if t in ("less_than_equal", "less_than"):
        return f"Maksimal {ctx.get('le', ctx.get('lt'))}"
    if t == "too_short":
        return f"Minimal {ctx.get('min_length')} item"
    if t == "too_long":
        return f"Maksimal {ctx.get('max_length')} item"
    if t == "value_error":  # dari field_validator: pakai pesan aslinya
        return str(ctx.get("error", err.get("msg", "Tidak valid")))
    return _MESSAGES.get(t, err.get("msg", "Tidak valid"))


def _field_path(loc: tuple[Any, ...]) -> str:
    # ("body", "items", 1, "quantity") → "items[1].quantity"; ("query", "limit") → "limit"
    parts = list(loc[1:]) if loc and loc[0] in ("body", "query", "path", "header") else list(loc)
    out = ""
    for p in parts:
        out += f"[{p}]" if isinstance(p, int) else (f".{p}" if out else str(p))
    return out or "body"


# ---------- Handler ----------


async def _app_error(_: Request, exc: AppError) -> JSONResponse:
    return error_response(exc.status, exc.code, exc.message, exc.details)


async def _validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    details = [
        {"field": _field_path(tuple(e.get("loc", ()))), "message": _translate(e)} for e in exc.errors()
    ]
    first = details[0] if details else None
    message = f"Input tidak valid: {first['field']} — {first['message']}" if first else "Input tidak valid"
    return error_response(422, "VALIDATION_ERROR", message, details)


async def _duplicate_key(_: Request, exc: DuplicateKeyError) -> JSONResponse:
    # Jaring pengaman: service sebaiknya menangkap DuplicateKeyError sendiri dengan pesan yang jelas.
    key = (exc.details or {}).get("keyValue") or {}
    field = next(iter(key), None)
    return error_response(409, "DUPLICATE", "Data sudah ada", [{"field": field}] if field else None)


_HTTP_CODES = {
    400: ("BAD_REQUEST", "Permintaan tidak valid"),
    401: ("UNAUTHORIZED", "Silakan login terlebih dahulu"),
    403: ("FORBIDDEN", "Anda tidak memiliki akses ke fitur ini"),
    404: ("NOT_FOUND", "Endpoint tidak ditemukan"),
    405: ("BAD_REQUEST", "Method tidak diizinkan untuk endpoint ini"),
}


async def _http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    code, message = _HTTP_CODES.get(exc.status_code, ("BAD_REQUEST", "Permintaan tidak valid"))
    response = error_response(exc.status_code, code, message)
    if exc.headers:
        response.headers.update(exc.headers)
    return response


async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path, exc_info=exc)
    return error_response(500, "INTERNAL_ERROR", "Terjadi kesalahan pada server")


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _app_error)
    app.add_exception_handler(RequestValidationError, _validation_error)
    app.add_exception_handler(DuplicateKeyError, _duplicate_key)
    app.add_exception_handler(StarletteHTTPException, _http_error)
    app.add_exception_handler(Exception, _unhandled)
