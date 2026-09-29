import type { BestSellerItem, StockItem, GrossProfitItem, CashflowItem } from '../types/report'

const bestSellers: BestSellerItem[] = [
  { productId: 'p1', name: 'Buku Tulis 38 Lembar', qty: 320, revenue: 1280000 },
  { productId: 'p2', name: 'Pulpen', qty: 280, revenue: 700000 },
  { productId: 'p3', name: 'Air Mineral 600ml', qty: 260, revenue: 780000 },
  { productId: 'p4', name: 'Mie Instan', qty: 210, revenue: 630000 },
  { productId: 'p5', name: 'Pensil 2B', qty: 190, revenue: 380000 },
  { productId: 'p6', name: 'Penghapus', qty: 150, revenue: 225000 },
  { productId: 'p7', name: 'Snack Ringan', qty: 140, revenue: 420000 },
  { productId: 'p8', name: 'Kopi Sachet', qty: 120, revenue: 240000 },
  { productId: 'p9', name: 'Buku Gambar', qty: 95, revenue: 380000 },
  { productId: 'p10', name: 'Map Plastik', qty: 80, revenue: 160000 },
]

// Meniru GET /reports/best-sellers
export function mockGetBestSellers(): Promise<BestSellerItem[]> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(bestSellers), 400)
  })
}

const stockItems: StockItem[] = [
  { productId: 'p1', name: 'Buku Tulis 38 Lembar', stock: 48, minimumStock: 20, stockStatus: 'AMAN' },
  { productId: 'p2', name: 'Pulpen', stock: 15, minimumStock: 20, stockStatus: 'MENIPIS' },
  { productId: 'p3', name: 'Air Mineral 600ml', stock: 60, minimumStock: 30, stockStatus: 'AMAN' },
  { productId: 'p4', name: 'Mie Instan', stock: 0, minimumStock: 25, stockStatus: 'HABIS' },
  { productId: 'p5', name: 'Pensil 2B', stock: 18, minimumStock: 20, stockStatus: 'MENIPIS' },
  { productId: 'p6', name: 'Penghapus', stock: 40, minimumStock: 15, stockStatus: 'AMAN' },
]

// Meniru GET /reports/stock
export function mockGetStockReport(): Promise<StockItem[]> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(stockItems), 400)
  })
}

const grossProfitItems: GrossProfitItem[] = [
  { period: 'Minggu 1', grossProfit: 1200000, margin: 22 },
  { period: 'Minggu 2', grossProfit: 1450000, margin: 24.5 },
  { period: 'Minggu 3', grossProfit: 980000, margin: 19 },
  { period: 'Minggu 4', grossProfit: 1600000, margin: 26 },
]

// Meniru GET /reports/gross-profit
export function mockGetGrossProfit(): Promise<GrossProfitItem[]> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(grossProfitItems), 400)
  })
}
const cashflowItems: CashflowItem[] = [
  { period: 'Sen', income: 850000, expense: 300000, net: 550000 },
  { period: 'Sel', income: 920000, expense: 410000, net: 510000 },
  { period: 'Rab', income: 780000, expense: 260000, net: 520000 },
  { period: 'Kam', income: 1010000, expense: 500000, net: 510000 },
  { period: 'Jum', income: 1200000, expense: 480000, net: 720000 },
  { period: 'Sab', income: 1350000, expense: 600000, net: 750000 },
  { period: 'Min', income: 600000, expense: 200000, net: 400000 },
]

// Meniru GET /reports/cashflow
export function mockGetCashflow(): Promise<CashflowItem[]> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(cashflowItems), 400)
  })
}