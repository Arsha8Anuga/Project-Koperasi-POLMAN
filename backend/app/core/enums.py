"""Enum sesuai dokumen 04 §4. Nilai string = nilai di JSON dan di MongoDB."""

from enum import StrEnum


class Role(StrEnum):
    OWNER = "OWNER"
    LOGISTIK = "LOGISTIK"
    ADMIN = "ADMIN"
    KASIR = "KASIR"
    MEMBER = "MEMBER"  # dicadangkan, belum dipakai


# Role yang boleh dibuat lewat /users (MEMBER belum dipakai).
STAFF_ROLES: tuple[Role, ...] = (Role.OWNER, Role.LOGISTIK, Role.ADMIN, Role.KASIR)


class App(StrEnum):
    KASIR = "KASIR"
    ADMIN = "ADMIN"


# Role yang boleh login ke masing-masing aplikasi (dokumen 04 §7.1).
APP_ROLES: dict[App, frozenset[Role]] = {
    App.KASIR: frozenset({Role.KASIR}),
    App.ADMIN: frozenset({Role.OWNER, Role.LOGISTIK, Role.ADMIN}),
}


class TransactionType(StrEnum):
    SALE = "SALE"
    RESTOCK = "RESTOCK"


class TransactionStatus(StrEnum):
    COMPLETED = "COMPLETED"
    PENDING = "PENDING"  # dicadangkan
    CANCELLED = "CANCELLED"  # dicadangkan
    EXPIRED = "EXPIRED"  # dicadangkan


class PaymentMethod(StrEnum):
    CASH = "CASH"
    QRIS = "QRIS"


class StockMovementType(StrEnum):
    SALE = "SALE"
    RESTOCK = "RESTOCK"
    ADJUSTMENT = "ADJUSTMENT"  # dicadangkan


class StockStatus(StrEnum):
    OK = "OK"
    LOW = "LOW"
    OUT = "OUT"


class Granularity(StrEnum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class AuditAction(StrEnum):
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DEACTIVATE = "DEACTIVATE"
    ACTIVATE = "ACTIVATE"
    RESET_PASSWORD = "RESET_PASSWORD"
    SALE = "SALE"
    RESTOCK = "RESTOCK"


class AuditModule(StrEnum):
    AUTH = "AUTH"
    USER = "USER"
    MEMBER = "MEMBER"
    CATEGORY = "CATEGORY"
    PRODUCT = "PRODUCT"
    SUPPLIER = "SUPPLIER"
    RESTOCK = "RESTOCK"
    SALE = "SALE"
