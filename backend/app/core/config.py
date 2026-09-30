"""Konfigurasi aplikasi, dibaca dari environment / file `.env` (lihat `.env.example`)."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    mongodb_uri: str = "mongodb://localhost:27017/?directConnection=true"
    mongodb_db: str = "koperasi_dev"
    # Dipakai pytest. DB ini DI-DROP setiap test, jadi beri nama sendiri per orang.
    test_mongodb_db: str = "koperasi_test"

    jwt_secret: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480

    # Folder foto produk yang diunggah. Docker: /app/media (named volume "media" di docker-compose.yml).
    media_root: str = "media"

    cors_origins: str = "http://localhost:5173,http://localhost:5174"
    app_tz: str = "Asia/Jakarta"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
