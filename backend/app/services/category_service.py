from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import DuplicateKeyError

from app.core.enums import AuditAction, AuditModule
from app.core.errors import duplicate, not_found
from app.repositories import category_repo
from app.schemas.auth import CurrentUser
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.services import audit_service as audit
from app.utils.objectid import parse_object_id
from app.utils.time import utcnow

_NOT_FOUND = "Kategori tidak ditemukan"


async def list_categories(db: AsyncDatabase, is_active: bool | None) -> list[CategoryOut]:
    filter = {} if is_active is None else {"isActive": is_active}
    return [CategoryOut.model_validate(d) for d in await category_repo.find_all(db, filter)]


async def create(db: AsyncDatabase, actor: CurrentUser, body: CategoryCreate) -> CategoryOut:
    now = utcnow()
    doc = {
        "name": body.name,
        "description": body.description,
        "isActive": True,
        "createdAt": now,
        "updatedAt": now,
    }
    try:
        doc = await category_repo.insert(db, doc)
    except DuplicateKeyError:
        raise duplicate(f"Kategori '{body.name}' sudah ada", "name") from None
    await audit.log(
        db, actor, AuditAction.CREATE, AuditModule.CATEGORY, doc["_id"], f"Membuat kategori {body.name}"
    )
    return CategoryOut.model_validate(doc)


async def update(
    db: AsyncDatabase, actor: CurrentUser, category_id: str, body: CategoryUpdate
) -> CategoryOut:
    old = await category_repo.find_by_id(db, parse_object_id(category_id, _NOT_FOUND))
    if old is None:
        raise not_found(_NOT_FOUND)
    try:
        doc = await category_repo.update(
            db,
            old["_id"],
            {
                "name": body.name,
                "description": body.description,
                "isActive": body.is_active,
                "updatedAt": utcnow(),
            },
        )
    except DuplicateKeyError:
        raise duplicate(f"Kategori '{body.name}' sudah ada", "name") from None

    if body.name != old["name"] or body.description != old.get("description"):
        await audit.log(
            db,
            actor,
            AuditAction.UPDATE,
            AuditModule.CATEGORY,
            old["_id"],
            f"Mengubah kategori {old['name']}"
            + (f" menjadi {body.name}" if body.name != old["name"] else ""),
        )
    if body.is_active != old["isActive"]:
        action = AuditAction.ACTIVATE if body.is_active else AuditAction.DEACTIVATE
        verb = "Mengaktifkan" if body.is_active else "Menonaktifkan"
        await audit.log(db, actor, action, AuditModule.CATEGORY, old["_id"], f"{verb} kategori {body.name}")
    return CategoryOut.model_validate(doc)
