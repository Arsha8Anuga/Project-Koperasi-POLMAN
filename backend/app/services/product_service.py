# app/services/product_service.py

# ---------- 1. IMPORT (sesuaikan path dengan repo lu) ----------
from app.repositories import category_repo, product_repo
from app.schemas.product import ProductOut
from app.utils.serialize import to_json
from app.utils.time import utcnow
from app.services import audit_service as audit
from app.core.errors import AppError


# ---------- 2. FUNGSI BANTU ----------
def stock_status(stock: int, minimum: int) -> str:
    if stock <= 0:
        return "OUT"
    return "LOW" if stock <= minimum else "OK"


def _out(doc: dict, category_name: str | None) -> dict:
    doc["categoryName"] = category_name
    doc["stockStatus"] = stock_status(doc["stock"], doc["minimumStock"])
    return ProductOut.model_validate(to_json(doc)).model_dump(by_alias=True)


# ---------- 3. FUNGSI UTAMA ----------
async def create(db, user, body):
    cat = await category_repo.find_by_id(db, body.category_id)
    if not cat:
        raise AppError(404, "NOT_FOUND", "Kategori tidak ditemukan")
    now = utcnow()
    doc = {"sku": body.sku.strip().upper(), "name": body.name.strip(),
           "categoryId": cat["_id"], "unit": body.unit,
           "sellingPrice": body.selling_price, "minimumStock": body.minimum_stock,
           "stock": 0, "costPrice": 0, "lastPurchasePrice": 0,   # selalu mulai dari 0!
           "imageUrl": body.image_url, "isActive": True, "createdAt": now, "updatedAt": now}
    if body.barcode:            # JEBAKAN: jangan simpan barcode=None
        doc["barcode"] = body.barcode

    doc = await product_repo.insert(db, doc)
    await audit.log(db, user, "CREATE", "PRODUCT", doc["_id"], f"Membuat produk {doc['sku']}")
    return _out(doc, cat["name"])