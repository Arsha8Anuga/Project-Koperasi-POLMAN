"""Mengisi IP client untuk audit log dan menulis log singkat per request.

Ditulis sebagai ASGI middleware murni (bukan BaseHTTPMiddleware) supaya contextvar
yang di-set di sini terlihat oleh handler endpoint.
"""

import logging
import time

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.utils.request_context import client_ip

logger = logging.getLogger("app.request")


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        ip = _client_ip(scope)
        token = client_ip.set(ip)
        start = time.perf_counter()
        status = 500

        async def send_wrapper(message: Message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            client_ip.reset(token)
            ms = (time.perf_counter() - start) * 1000
            logger.info("%s %s %s %d %.0fms", ip, scope["method"], scope["path"], status, ms)


def _client_ip(scope: Scope) -> str | None:
    # X-Forwarded-For sengaja TIDAK dibaca: tanpa reverse proxy, header itu bisa dipalsukan
    # siapa saja dan mengotori audit trail. Kalau nanti pakai nginx, jalankan uvicorn dengan
    # `--proxy-headers --forwarded-allow-ips=<ip-nginx>` — uvicorn yang mengisi scope["client"].
    client = scope.get("client")
    return client[0] if client else None
