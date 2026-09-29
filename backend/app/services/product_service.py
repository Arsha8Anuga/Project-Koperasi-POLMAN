from typing import Any

from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import DuplicateKeyError

from app.core.enums import AuditAction, AuditModule, Role, StockStatus
from app.core.errors import AppError, duplicate, not_found
from app.repositories import category_repo, product_repo
from app.schemas.auth import CurrentUser
from app.schemas.product import ProductCreate, ProductOut, ProductStatusUpdate, ProductUpdate
from app.services import audit_service as audit
from app.utils.objectid import optional_object_id, parse_object_id
from app.utils.pagination import PageParams
from app.utils.text import search_regex
from app.utils.time import utcnow

_NOT_FOUND = "Produk tidak ditemukan"
_COST_FIELDS = {"cost_price", "last_purchase_price"}


def stock_status(stock: int, minimum_stock: int) -> StockStatus:
    """OUT: stok 0. LOW: 0 < stok <= minimum. OK: sisanya. Sama dengan product_repo.STOCK_STATUS_FILTERS."""
    if stock <= 0:
        return StockStatus.OUT
    return StockStatus.LOW if stock <= minimum_stock else StockStatus.OK


def present(doc: dict[str, Any], category_name: str | None, viewer: CurrentUser) -> dict[str, Any]:
    """Dokumen → JSON. KASIR tidak boleh melihat harga pokok (dokumen 04 §5)."""
    model = ProductOut.model_validate(
        {**doc, "categoryName": category_name, "stockStatus": stock_status(doc["stock"], doc["minimumStock"])}
    )
    exclude = _COST_FIELDS if viewer.role == Role.KASIR else None
    return model.model_dump(by_alias=True, mode="json", exclude=exclude)


def _duplicate_error(exc: DuplicateKeyError, body: ProductCreate) -> AppError:
    details = exc.details or {}
    key = details.get("keyValue") or details.get("keyPattern") or {}
    if "barcode" in key or (not key and "barcode" in str(exc)):
        return duplicate(f"Barcode '{body.barcode}' sudah dipakai produk lain", "barcode")
    return duplicate(f"SKU '{body.sku}' sudah dipakai", "sku")


async def _check_unique(db: AsyncDatabase, body: ProductCreate, exclude_id=None) -> None:
    """Cek SKU/barcode lebih dulu supaya pesan 409 menyebut field yang tepat.
    Index unik tetap jadi pengaman terakhir kalau dua request bersamaan lolos cek ini."""
    not_self = {"_id": {"$ne": exclude_id}} if exclude_id else {}
    if await product_repo.find_one(db, {"sku": body.sku, **not_self}):
        raise duplicate(f"SKU '{body.sku}' sudah dipakai", "sku")
    if body.barcode and await product_repo.find_one(db, {"barcode": body.barcode, **not_self}):
        raise duplicate(f"Barcode '{body.barcode}' sudah dipakai produk lain", "barcode")


async def _category_or_error(db: AsyncDatabase, category_id: str) -> dict[str, Any]:
    category = await category_repo.find_by_id(db, parse_object_id(category_id))
    if category is None:
        raise AppError(
            422,
            "VALIDATION_ERROR",
            "Kategori tidak ditemukan",
            [{"field": "categoryId", "message": "Tidak ada"}],
        )
    return category


async def _get_or_404(db: AsyncDatabase, product_id: str) -> dict[str, Any]:
    doc = await product_repo.find_by_id(db, parse_object_id(product_id, _NOT_FOUND))
    if doc is None:
        raise not_found(_NOT_FOUND)
    return doc


async def list_products(
    db: AsyncDatabase,
    viewer: CurrentUser,
    page: PageParams,
    search: str | None,
    category_id: str | None,
    is_active: bool | None,
    status: StockStatus | None,
    sort: str,
) -> tuple[list[dict[str, Any]], int]:
    filter: dict[str, Any] = {}
    if viewer.role == Role.KASIR:
        is_active = True  # kasir hanya boleh melihat produk aktif, apa pun query-nya
    if is_active is not None:
        filter["isActive"] = is_active
    if cat := optional_object_id(category_id, "categoryId"):
        filter["categoryId"] = cat
    if search and search.strip():
        rx = search_regex(search)
        filter["$or"] = [{"name": rx}, {"sku": rx}, {"barcode": rx}]
    if status:
        filter.update(product_repo.STOCK_STATUS_FILTERS[str(status)])

    docs, total = await product_repo.list_page(db, filter, page, sort)
    names = await category_repo.name_map(db)
    return [present(d, names.get(d["categoryId"]), viewer) for d in docs], total


async def get_product(db: AsyncDatabase, viewer: CurrentUser, product_id: str) -> dict[str, Any]:
    doc = await _get_or_404(db, product_id)
    if viewer.role == Role.KASIR and not doc["isActive"]:
        raise not_found(_NOT_FOUND)
    category = await category_repo.find_by_id(db, doc["categoryId"])
    return present(doc, category["name"] if category else None, viewer)


def _fields(body: ProductCreate, category: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    fields = {
        "sku": body.sku,
        "name": body.name,
        "categoryId": category["_id"],
        "unit": body.unit,
        "sellingPrice": body.selling_price,
        "minimumStock": body.minimum_stock,
        "imageUrl": body.image_url,
    }
    # Barcode kosong TIDAK disimpan sama sekali (index unik hanya untuk barcode bertipe string).
    if body.barcode:
        fields["barcode"] = body.barcode
        return fields, []
    return fields, ["barcode"]


async def create(db: AsyncDatabase, actor: CurrentUser, body: ProductCreate) -> dict[str, Any]:
    category = await _category_or_error(db, body.category_id)
    await _check_unique(db, body)
    fields, _ = _fields(body, category)
    now = utcnow()
    doc = {
        **fields,
        # Produk baru selalu mulai dari 0; stok hanya bertambah lewat restock.
        "stock": 0,
        "costPrice": 0,
        "lastPurchasePrice": 0,
        "isActive": True,
        "createdAt": now,
        "updatedAt": now,
    }
    try:
        doc = await product_repo.insert(db, doc)
    except DuplicateKeyError as exc:
        raise _duplicate_error(exc, body) from None
    await audit.log(
        db,
        actor,
        AuditAction.CREATE,
        AuditModule.PRODUCT,
        doc["_id"],
        f"Membuat produk {body.sku} - {body.name}",
    )
    return present(doc, category["name"], actor)


async def update(
    db: AsyncDatabase, actor: CurrentUser, product_id: str, body: ProductUpdate
) -> dict[str, Any]:
    old = await _get_or_404(db, product_id)
    category = await _category_or_error(db, body.category_id)
    await _check_unique(db, body, exclude_id=old["_id"])
    fields, unset = _fields(body, category)
    try:
        doc = await product_repo.update(db, old["_id"], {**fields, "updatedAt": utcnow()}, unset)
    except DuplicateKeyError as exc:
        raise _duplicate_error(exc, body) from None

    if body.selling_price != old["sellingPrice"]:
        await audit.log(
            db,
            actor,
            AuditAction.UPDATE,
            AuditModule.PRODUCT,
            old["_id"],
            f"Mengubah harga jual {body.sku} dari {old['sellingPrice']} menjadi {body.selling_price}",
        )
    changed = [k for k, v in fields.items() if k != "sellingPrice" and old.get(k) != v]
    if changed or (unset and "barcode" in old):
        await audit.log(
            db, actor, AuditAction.UPDATE, AuditModule.PRODUCT, old["_id"], f"Mengubah data produk {body.sku}"
        )
    return present(doc, category["name"], actor)


async def set_status(
    db: AsyncDatabase, actor: CurrentUser, product_id: str, body: ProductStatusUpdate
) -> dict[str, Any]:
    old = await _get_or_404(db, product_id)
    doc = old
    if old["isActive"] != body.is_active:
        doc = await product_repo.update(db, old["_id"], {"isActive": body.is_active, "updatedAt": utcnow()})
        action = AuditAction.ACTIVATE if body.is_active else AuditAction.DEACTIVATE
        verb = "Mengaktifkan" if body.is_active else "Menonaktifkan"
        await audit.log(db, actor, action, AuditModule.PRODUCT, old["_id"], f"{verb} produk {old['sku']}")
    category = await category_repo.find_by_id(db, doc["categoryId"])
    return present(doc, category["name"] if category else None, actor)
