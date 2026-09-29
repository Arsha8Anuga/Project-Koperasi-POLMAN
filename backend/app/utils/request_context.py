"""Data per-request yang dibutuhkan service tanpa menyentuh `Request` FastAPI.

Middleware `RequestContextMiddleware` mengisi IP client; `audit.log` membacanya
sendiri, jadi service BE-2/BE-3 tidak perlu meneruskan IP ke mana-mana.
"""

from contextvars import ContextVar

client_ip: ContextVar[str | None] = ContextVar("client_ip", default=None)
