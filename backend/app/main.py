import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.db import mongo
from app.db.indexes import ensure_indexes
from app.middlewares.error_handler import register_exception_handlers
from app.middlewares.request_context import RequestContextMiddleware
from app.utils.response import ok

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    await mongo.connect(settings.mongodb_uri, settings.mongodb_db)
    await ensure_indexes(mongo.get_database())
    yield
    await mongo.close()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Koperasi API", version="0.1.0", lifespan=lifespan)

    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)

    @app.get("/health", tags=["health"])
    async def health():
        await mongo.get_client().admin.command("ping")
        return ok({"db": mongo.get_database().name})

    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
