"""Dashboard LOGISTIK — milik BE-2.

TODO(BE-2): ganti angka 0 dengan hitungan sungguhan:
  activeProducts     = produk isActive=true
  lowStockCount      = aktif, 0 < stock <= minimumStock
  outOfStockCount    = aktif, stock = 0
  restocksThisMonth  = transaksi RESTOCK sejak tanggal 1 bulan ini (WIB)
"""

from pymongo.asynchronous.database import AsyncDatabase

from app.schemas.dashboard import LogistikSummary


async def logistik_summary(db: AsyncDatabase) -> LogistikSummary:
    return LogistikSummary(active_products=0, low_stock_count=0, out_of_stock_count=0, restocks_this_month=0)
