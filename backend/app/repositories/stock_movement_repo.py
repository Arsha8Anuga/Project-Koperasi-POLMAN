from typing import Any

from pymongo.asynchronous.database import AsyncDatabase

from app.repositories.base import find_page
from app.utils.pagination import PageParams


def _col(db: AsyncDatabase):
    return db["stock_movements"]


async def insert_many(db: AsyncDatabase, docs: list[dict[str, Any]], session=None) -> None:
    if docs:
        await _col(db).insert_many(docs, session=session)


async def list_page(
    db: AsyncDatabase, filter: dict[str, Any], page: PageParams
) -> tuple[list[dict[str, Any]], int]:
    return await find_page(_col(db), filter, page, sort=[("createdAt", -1), ("_id", -1)])
