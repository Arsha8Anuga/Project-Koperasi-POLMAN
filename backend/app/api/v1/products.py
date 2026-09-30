"""Tanpa `response_model`: isi response bergantung role (KASIR tidak menerima harga pokok),
jadi service mengembalikan dict yang sudah dibentuk."""

from typing import Literal

from fastapi import APIRouter, Depends, Query, Request
from pymongo.asynchronous.database import AsyncDatabase

from app.api.deps import CurrentUser, get_db, require_roles
from app.core.enums import Role, StockStatus
from app.schemas.common import ERROR_RESPONSES
from app.schemas.product import ProductCreate, ProductStatusUpdate, ProductUpdate
from app.services import product_image_service, product_service
from app.utils.pagination import PageParams
from app.utils.response import ok, paginated

router = APIRouter(prefix="/products", tags=["products"], responses=ERROR_RESPONSES)
viewers = require_roles(Role.KASIR, Role.LOGISTIK, Role.OWNER)
logistik_only = require_roles(Role.LOGISTIK)


@router.get("")
async def list_products(
    page: PageParams = Depends(),
    search: str | None = Query(None, max_length=64, description="nama / SKU / barcode"),
    category_id: str | None = Query(None, alias="categoryId"),
    is_active: bool | None = Query(None, alias="isActive", description="diabaikan untuk KASIR"),
    stock_status: StockStatus | None = Query(None, alias="stockStatus"),
    sort: Literal["name", "-stock", "stock", "-createdAt"] = "name",
    user: CurrentUser = Depends(viewers),
    db: AsyncDatabase = Depends(get_db),
):
    items, total = await product_service.list_products(
        db, user, page, search, category_id, is_active, stock_status, sort
    )
    return paginated(items, page, total)


# Didefinisikan SEBELUM /{product_id} supaya "lookup" tidak dianggap ID.
@router.get("/lookup/{code}")
async def lookup_product(
    code: str, user: CurrentUser = Depends(viewers), db: AsyncDatabase = Depends(get_db)
):
    """Hasil scan barcode (scanner USB, kamera, atau ketik manual): barcode persis, lalu SKU persis.
    KASIR hanya mendapat produk aktif."""
    return ok(await product_service.lookup_by_code(db, user, code))


@router.get("/{product_id}")
async def get_product(
    product_id: str, user: CurrentUser = Depends(viewers), db: AsyncDatabase = Depends(get_db)
):
    return ok(await product_service.get_product(db, user, product_id))


@router.post("", status_code=201)
async def create_product(
    body: ProductCreate, user: CurrentUser = Depends(logistik_only), db: AsyncDatabase = Depends(get_db)
):
    return ok(await product_service.create(db, user, body), "Produk berhasil dibuat")


@router.put("/{product_id}")
async def update_product(
    product_id: str,
    body: ProductUpdate,
    user: CurrentUser = Depends(logistik_only),
    db: AsyncDatabase = Depends(get_db),
):
    return ok(await product_service.update(db, user, product_id, body), "Produk berhasil diperbarui")


@router.patch("/{product_id}/status")
async def set_product_status(
    product_id: str,
    body: ProductStatusUpdate,
    user: CurrentUser = Depends(logistik_only),
    db: AsyncDatabase = Depends(get_db),
):
    result = await product_service.set_status(db, user, product_id, body)
    return ok(result, "Produk berhasil diaktifkan" if body.is_active else "Produk berhasil dinonaktifkan")


async def _read_limited(request: Request, limit: int) -> bytes:
    """Baca body mentah dengan batas ukuran (tanpa multipart: tidak perlu python-multipart)."""
    declared = request.headers.get("content-length")
    if declared and declared.isdigit() and int(declared) > limit:
        raise product_image_service.too_large()
    chunks, size = [], 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > limit:
            raise product_image_service.too_large()
        chunks.append(chunk)
    return b"".join(chunks)


@router.put(
    "/{product_id}/image",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                t: {"schema": {"type": "string", "format": "binary"}}
                for t in ("image/jpeg", "image/png", "image/webp")
            },
        }
    },
)
async def upload_product_image(
    product_id: str,
    request: Request,
    user: CurrentUser = Depends(logistik_only),
    db: AsyncDatabase = Depends(get_db),
):
    """Body = isi file gambar (JPEG/PNG/WebP, maks 1,5 MB). Foto lama milik produk ini ikut dihapus."""
    data = await _read_limited(request, product_image_service.MAX_IMAGE_BYTES)
    return ok(await product_image_service.set_image(db, user, product_id, data), "Foto produk disimpan")


@router.delete("/{product_id}/image")
async def delete_product_image(
    product_id: str, user: CurrentUser = Depends(logistik_only), db: AsyncDatabase = Depends(get_db)
):
    return ok(await product_image_service.remove_image(db, user, product_id), "Foto produk dihapus")
