"""Dependency bersama untuk SEMUA router.

from app.api.deps import CurrentUser, get_client, get_db, require_roles
"""

from app.api.deps.auth import get_current_user, require_roles
from app.api.deps.database import get_client, get_db
from app.schemas.auth import CurrentUser

__all__ = ["CurrentUser", "get_client", "get_current_user", "get_db", "require_roles"]
