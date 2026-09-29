# app/repositories/product_repo.py
async def insert(db, doc: dict):
    res = await db.products.insert_one(doc)
    doc["_id"] = res.inserted_id
    return doc

# tambahin di app/repositories/product_repo.py
async def find_active(db, category_id: str | None = None):
    q = {"isActive": True}
    if category_id:
        q["categoryId"] = to_oid(category_id)
    return await db.products.find(q).sort("name", 1).to_list()