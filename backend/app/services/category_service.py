from app.repositories import category_repo
from app.schemas.category import CategoryOut
from app.utils.serialize import to_json
from app.utils.time import utcnow            # sesuaikan
from app.services import audit_service as audit_ser               # punya BE-1
from app.core.errors import AppError

def _out(doc):
    return CategoryOut.model_validate(to_json(doc)).model_dump(by_alias=True)

async def list_all(db, is_active):
    return [_out(d) for d in await category_repo.find_all(db, is_active)]

async def create(db, user, body):
    now = utcnow()
    doc = {"name": body.name.strip(), "description": body.description,
           "isActive": True, "createdAt": now, "updatedAt": now}
    doc = await category_repo.insert(db, doc)
    await audit.log(db, user, "CREATE", "CATEGORY", doc["_id"], f"Membuat kategori {doc['name']}")
    return _out(doc)

async def update(db, user, id, body):
    old = await category_repo.find_by_id(db, id)
    if not old:
        raise AppError(404, "NOT_FOUND", "Kategori tidak ditemukan")
    doc = await category_repo.update(db, id, {
        "name": body.name.strip(), "description": body.description,
        "isActive": body.is_active, "updatedAt": utcnow()})
    action = "UPDATE" if body.is_active == old["isActive"] else ("ACTIVATE" if body.is_active else "DEACTIVATE")
    await audit.log(db, user, action, "CATEGORY", doc["_id"], f"Mengubah kategori {doc['name']}")
    return _out(doc)
