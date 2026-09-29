# app/api/v1/products.py
from fastapi import APIRouter, Depends  # pyright: ignore[reportMissingImports]
from app.api.deps import get_db, require_roles
from app.core.enums import Role
from app.schemas.product import ProductCreate
from app.services import product_service
from app.utils.response import ok

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("", status_code=201)
async def create_product(body: ProductCreate,
                         user=Depends(require_roles(Role.LOGISTIK)), db=Depends(get_db)):
    return ok(await product_service.create(db, user, body), "Produk berhasil dibuat")