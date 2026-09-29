"""Dashboard OWNER — milik BE-3.

TODO(BE-3): ganti angka 0 dengan hitungan sungguhan (hari ini = WIB, lihat app.utils.time):
  salesToday         = Σ total SALE hari ini
  transactionsToday  = jumlah SALE hari ini
  grossProfitToday   = Σ (items.subtotal − items.quantity × items.costPrice) SALE hari ini
  restockToday       = Σ total RESTOCK hari ini
"""

from pymongo.asynchronous.database import AsyncDatabase

from app.schemas.dashboard import OwnerSummary


async def owner_summary(db: AsyncDatabase) -> OwnerSummary:
    return OwnerSummary(sales_today=0, transactions_today=0, gross_profit_today=0, restock_today=0)
