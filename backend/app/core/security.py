"""Hash password (bcrypt, cost 12) dan JWT HS256 (dokumen 05 §4)."""

from datetime import UTC, datetime, timedelta
from typing import Any

import anyio
import bcrypt
import jwt

from app.core.config import get_settings

BCRYPT_ROUNDS = 12


# ---------- Password ----------
# bcrypt sengaja lambat (~0,2 detik) dan memblokir CPU, jadi di endpoint async
# pakai versi `a...` supaya dijalankan di thread pool dan tidak membekukan server.


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=BCRYPT_ROUNDS)).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ValueError:  # hash rusak / bukan bcrypt
        return False


async def ahash_password(password: str) -> str:
    return await anyio.to_thread.run_sync(hash_password, password)


async def averify_password(password: str, password_hash: str) -> bool:
    return await anyio.to_thread.run_sync(verify_password, password, password_hash)


# Hash asal-asalan untuk login dengan username yang tidak ada: tetap menjalankan bcrypt
# supaya waktu respons sama, sehingga penyerang tidak bisa menebak username yang valid.
_DUMMY_HASH: str | None = None


async def averify_dummy(password: str) -> None:
    global _DUMMY_HASH
    if _DUMMY_HASH is None:
        _DUMMY_HASH = await ahash_password("dummy-password-untuk-timing")
    await averify_password(password, _DUMMY_HASH)


# ---------- JWT ----------


class TokenError(Exception):
    """Token tidak ada, rusak, atau kadaluarsa."""


def create_access_token(user_id: str, role: str, name: str) -> tuple[str, datetime]:
    settings = get_settings()
    expires_at = datetime.now(UTC).replace(microsecond=0) + timedelta(minutes=settings.jwt_expire_minutes)
    payload: dict[str, Any] = {"sub": user_id, "role": role, "name": name, "exp": expires_at}
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, expires_at


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp"]},
        )
    except jwt.PyJWTError as exc:
        raise TokenError(str(exc)) from exc
    return payload
