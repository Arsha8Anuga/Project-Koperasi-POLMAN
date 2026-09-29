"""Helper query yang dipakai semua repository."""

from typing import Any

from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.asynchronous.collection import AsyncCollection

from app.utils.pagination import PageParams

Sort = list[tuple[str, int]]


async def find_page(
    collection: AsyncCollection,
    filter: dict[str, Any],
    page: PageParams,
    sort: Sort,
    projection: dict[str, Any] | None = None,
    session: AsyncClientSession | None = None,
) -> tuple[list[dict[str, Any]], int]:
    """Satu halaman data + total. `sort` sebaiknya diakhiri `_id` supaya urutan stabil antar halaman."""
    total = await collection.count_documents(filter, session=session)
    cursor = collection.find(filter, projection, session=session).sort(sort).skip(page.skip).limit(page.limit)
    return await cursor.to_list(), total
