from typing import Any

from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.asynchronous.database import AsyncDatabase

from app.repositories.base import find_page
from app.utils.pagination import PageParams


def _col(db: AsyncDatabase):
    return db["audit_logs"]


async def insert(db: AsyncDatabase, doc: dict[str, Any], session: AsyncClientSession | None = None) -> None:
    await _col(db).insert_one(doc, session=session)


async def list_page(
    db: AsyncDatabase, filter: dict[str, Any], page: PageParams
) -> tuple[list[dict[str, Any]], int]:
    return await find_page(_col(db), filter, page, sort=[("createdAt", -1), ("_id", -1)])


async def count(db: AsyncDatabase, filter: dict[str, Any]) -> int:
    return await _col(db).count_documents(filter)
