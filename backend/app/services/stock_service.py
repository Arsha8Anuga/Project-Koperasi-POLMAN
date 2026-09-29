# app/services/stock_service.py
from app.repositories import category_repo, product_repo
from app.services.product_service import stock_status
from app.repositories import stock_movement_repo
from app.services.restock_service import _range_utc
from app.utils.serialize import to_json

async def list_movements(db, product_id, type_, date_from, date_to, page, limit):
    limit = min(limit, 100)
    start, end = _range_utc(date_from, date_to)
    docs, total = await stock_movement_repo.find_page(
        db, product_id, type_, start, end, (page - 1) * limit, limit)
    return [to_json(d) for d in docs], total, limit

async def stock_report(db, category_id, status):
    products = await product_repo.find_active(db, category_id)
    cats = {c["_id"]: c["name"] for c in await category_repo.find_all(db, None)}
    counts = {"OK": 0, "LOW": 0, "OUT": 0}
    items = []
    for p in products:
        s = stock_status(p["stock"], p["minimumStock"])
        counts[s] += 1
        if status and s != status:
            continue
        items.append({"productId": str(p["_id"]), "sku": p["sku"], "name": p["name"],
                      "categoryName": cats.get(p["categoryId"]), "stock": p["stock"],
                      "minimumStock": p["minimumStock"], "stockStatus": s})
    return {"items": items, "counts": counts}