"""Foto produk yang diunggah LOGISTIK, disimpan sebagai FILE di disk (bukan di MongoDB).

Alur: frontend memperkecil foto di browser (maks 1024 px) → PUT /products/{id}/image (body = biner
gambar, bukan multipart) → ditulis ke `{MEDIA_ROOT}/product-images/{id}.{ext}` → `products.imageUrl`
diisi `/api/v1/product-images/{id}.{ext}`. URL gambar luar (http/https) tetap bisa dipakai seperti biasa;
kalau produk tidak punya gambar atau gambar gagal dimuat, frontend menampilkan placeholder.

Di Docker, MEDIA_ROOT (/app/media) adalah named volume, jadi foto tidak hilang saat container
di-redeploy. Nama file = ObjectId baru setiap unggah → isi file tidak pernah berubah (aman di-cache).
"""

import os
from pathlib import Path
from typing import Any

import anyio
from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.core.config import get_settings
from app.core.enums import AuditAction, AuditModule
from app.core.errors import AppError, not_found
from app.repositories import category_repo, product_repo
from app.schemas.auth import CurrentUser
from app.schemas.product import INTERNAL_IMAGE_PREFIX, INTERNAL_IMAGE_RE
from app.services import audit_service as audit
from app.services.product_service import _get_or_404, present
from app.utils.time import utcnow

MAX_IMAGE_BYTES = 1_500_000  # sudah diperkecil di browser; nginx sendiri membatasi 2 MB
EXTENSIONS = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
CONTENT_TYPES = {ext: ctype for ctype, ext in EXTENSIONS.items()}


def media_dir() -> Path:
    return Path(get_settings().media_root) / "product-images"


def detect_type(data: bytes) -> str | None:
    """Jenis gambar dari isi file (magic bytes), bukan dari header yang dikirim klien."""
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def internal_file_name(image_url: str | None) -> str | None:
    """`/api/v1/product-images/<id>.<ext>` → `<id>.<ext>`. Selain itu None (URL luar / kosong)."""
    if image_url and INTERNAL_IMAGE_RE.fullmatch(image_url):
        return image_url.removeprefix(INTERNAL_IMAGE_PREFIX)
    return None


def _write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)  # atomik: file tidak pernah terbaca setengah jadi


def _remove(name: str | None) -> None:
    if name:
        (media_dir() / name).unlink(missing_ok=True)


def too_large() -> AppError:
    return AppError(
        413,
        "PAYLOAD_TOO_LARGE",
        f"Ukuran foto maksimal {MAX_IMAGE_BYTES // 1000} KB",
        [{"field": "image", "maxBytes": MAX_IMAGE_BYTES}],
    )


async def _present(db: AsyncDatabase, doc: dict[str, Any], actor: CurrentUser) -> dict[str, Any]:
    category = await category_repo.find_by_id(db, doc["categoryId"])
    return present(doc, category["name"] if category else None, actor)


async def set_image(db: AsyncDatabase, actor: CurrentUser, product_id: str, data: bytes) -> dict[str, Any]:
    product = await _get_or_404(db, product_id)
    if not data:
        raise AppError(400, "BAD_REQUEST", "File foto kosong", [{"field": "image"}])
    if len(data) > MAX_IMAGE_BYTES:
        raise too_large()
    content_type = detect_type(data)
    if content_type is None:
        raise AppError(
            415, "UNSUPPORTED_MEDIA_TYPE", "Foto harus berformat JPEG, PNG, atau WebP", [{"field": "image"}]
        )

    name = f"{ObjectId()}.{EXTENSIONS[content_type]}"
    try:
        await anyio.to_thread.run_sync(_write, media_dir() / name, data)
    except OSError as exc:
        raise AppError(500, "STORAGE_ERROR", "Foto gagal disimpan di server") from exc
    doc = await product_repo.update(
        db, product["_id"], {"imageUrl": f"{INTERNAL_IMAGE_PREFIX}{name}", "updatedAt": utcnow()}
    )
    await anyio.to_thread.run_sync(_remove, internal_file_name(product.get("imageUrl")))
    await audit.log(
        db,
        actor,
        AuditAction.UPDATE,
        AuditModule.PRODUCT,
        product["_id"],
        f"Mengganti foto produk {product['sku']}",
    )
    return await _present(db, doc, actor)


async def remove_image(db: AsyncDatabase, actor: CurrentUser, product_id: str) -> dict[str, Any]:
    product = await _get_or_404(db, product_id)
    if not product.get("imageUrl"):
        return await _present(db, product, actor)
    doc = await product_repo.update(db, product["_id"], {"imageUrl": None, "updatedAt": utcnow()})
    await anyio.to_thread.run_sync(_remove, internal_file_name(product.get("imageUrl")))
    await audit.log(
        db,
        actor,
        AuditAction.UPDATE,
        AuditModule.PRODUCT,
        product["_id"],
        f"Menghapus foto produk {product['sku']}",
    )
    return await _present(db, doc, actor)


async def delete_if_unused(db: AsyncDatabase, old_url: str | None, new_url: str | None) -> None:
    """Dipanggil setelah PUT /products/{id}: foto lama yang diganti URL lain tidak dibiarkan menumpuk."""
    if old_url != new_url:
        await anyio.to_thread.run_sync(_remove, internal_file_name(old_url))


def image_path(file_name: str) -> tuple[Path, str]:
    """Path file + content-type. Nama divalidasi ketat (tidak bisa keluar folder: '../', dll.)."""
    if not INTERNAL_IMAGE_RE.fullmatch(f"{INTERNAL_IMAGE_PREFIX}{file_name}"):
        raise not_found("Foto tidak ditemukan")
    path = media_dir() / file_name
    if not path.is_file():
        raise not_found("Foto tidak ditemukan")
    return path, CONTENT_TYPES[file_name.rsplit(".", 1)[1]]
