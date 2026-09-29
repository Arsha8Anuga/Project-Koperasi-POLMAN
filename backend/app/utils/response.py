"""Pembungkus response sukses (dokumen 04 §2). Router SELALU mengembalikan salah satu dari ini.

return ok(user, "User berhasil dibuat")
return paginated(items, page, total)
return paginated(items, page, total, summary={...})   # field tambahan sejajar `meta`
"""

import math
from typing import Any

from app.utils.pagination import PageParams


def ok(data: Any = None, message: str = "OK") -> dict[str, Any]:
    return {"success": True, "message": message, "data": data}


def paginated(
    items: list[Any], page: PageParams, total: int, message: str = "OK", **extra: Any
) -> dict[str, Any]:
    return {
        "success": True,
        "message": message,
        "data": items,
        "meta": {
            "page": page.page,
            "limit": page.limit,
            "total": total,
            "totalPages": math.ceil(total / page.limit) if total else 0,
        },
        **extra,
    }
