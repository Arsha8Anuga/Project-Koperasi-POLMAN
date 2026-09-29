"""Parameter pagination standar (dokumen 04 §1): page mulai 1, limit default 20, maks 100.

Pemakaian di router:
    async def list_x(page: PageParams = Depends(), ...):
        items, total = await x_repo.find_page(db, filter, page)
        return paginated(items, page, total)
"""

from dataclasses import dataclass

from fastapi import Query


@dataclass
class PageParams:
    page: int = Query(1, ge=1, description="Halaman, mulai dari 1")
    limit: int = Query(20, ge=1, le=100, description="Jumlah per halaman (maks 100)")

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.limit
