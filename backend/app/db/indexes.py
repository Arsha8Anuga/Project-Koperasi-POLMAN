"""Index dibuat saat startup (idempoten). Revisi dari dokumen 05 §3.2:

1. `products.barcode`: partial index (hanya jika barcode berupa string), BUKAN sparse.
   Sparse tetap mengindeks `barcode: null`, jadi produk kedua tanpa barcode akan kena 409.
   Tetap disarankan: jangan simpan field `barcode` sama sekali kalau kosong.
2. Text index `products(name, sku)` DIHAPUS. Text index tidak bisa cocok sebagian
   ("buk" tidak menemukan "Buku"), sedangkan kontrak minta cocok sebagian → pakai `$regex`.
"""

from pymongo import ASCENDING, DESCENDING, IndexModel
from pymongo.asynchronous.database import AsyncDatabase

INDEXES: dict[str, list[IndexModel]] = {
    "users": [
        IndexModel([("username", ASCENDING)], unique=True, name="uniq_username"),
        IndexModel([("role", ASCENDING), ("isActive", ASCENDING)], name="role_active"),
    ],
    "members": [
        IndexModel([("memberNumber", ASCENDING)], unique=True, name="uniq_member_number"),
        IndexModel([("name", ASCENDING)], name="name"),
    ],
    "categories": [
        IndexModel([("name", ASCENDING)], unique=True, name="uniq_name"),
    ],
    "products": [
        IndexModel([("sku", ASCENDING)], unique=True, name="uniq_sku"),
        IndexModel(
            [("barcode", ASCENDING)],
            unique=True,
            partialFilterExpression={"barcode": {"$type": "string"}},
            name="uniq_barcode_if_string",
        ),
        IndexModel([("categoryId", ASCENDING)], name="category"),
        IndexModel([("isActive", ASCENDING)], name="active"),
    ],
    "suppliers": [
        IndexModel([("supplierCode", ASCENDING)], unique=True, name="uniq_supplier_code"),
        IndexModel([("name", ASCENDING)], name="name"),
    ],
    "transactions": [
        IndexModel([("code", ASCENDING)], unique=True, name="uniq_code"),
        IndexModel([("type", ASCENDING), ("createdAt", DESCENDING)], name="type_created"),
        IndexModel([("cashier.id", ASCENDING), ("createdAt", DESCENDING)], name="cashier_created"),
        IndexModel([("supplier.id", ASCENDING)], name="supplier"),
        IndexModel([("member.id", ASCENDING)], name="member"),
        IndexModel([("items.productId", ASCENDING)], name="item_product"),
    ],
    "stock_movements": [
        IndexModel([("productId", ASCENDING), ("createdAt", DESCENDING)], name="product_created"),
    ],
    "audit_logs": [
        IndexModel([("createdAt", DESCENDING)], name="created"),
        IndexModel([("user.id", ASCENDING), ("createdAt", DESCENDING)], name="user_created"),
        IndexModel([("module", ASCENDING), ("createdAt", DESCENDING)], name="module_created"),
    ],
}


async def ensure_indexes(db: AsyncDatabase) -> None:
    for collection, models in INDEXES.items():
        await db[collection].create_indexes(models)
