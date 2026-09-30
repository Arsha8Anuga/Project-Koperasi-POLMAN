"""GET /product-images/{file}: menyajikan foto produk yang diunggah (file di MEDIA_ROOT).

Sengaja TANPA login: tag <img> di browser tidak bisa mengirim header Authorization. Foto produk
bukan data rahasia, dan nama file acak (ObjectId baru setiap unggah), jadi tidak bisa ditebak berurutan.
Karena setiap unggah menghasilkan nama baru, isi file tidak pernah berubah → boleh di-cache selamanya.
"""

from fastapi import APIRouter, Request, Response
from fastapi.responses import FileResponse

from app.schemas.common import ERROR_RESPONSES
from app.services import product_image_service

router = APIRouter(prefix="/product-images", tags=["products"], responses=ERROR_RESPONSES)


@router.get("/{file_name}", response_class=FileResponse)
async def get_product_image(file_name: str, request: Request):
    path, content_type = product_image_service.image_path(file_name)
    etag = f'"{file_name}"'  # nama file unik per unggahan = isi tidak pernah berubah
    headers = {
        "Cache-Control": "public, max-age=31536000, immutable",
        "ETag": etag,
        "X-Content-Type-Options": "nosniff",
    }
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers=headers)
    return FileResponse(path, media_type=content_type, headers=headers)
