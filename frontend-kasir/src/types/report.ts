export type Granularity = 'HARIAN' | 'MINGGUAN' | 'BULANAN' | 'TAHUNAN'

export interface ReportParams {
  granularity: Granularity
  from: string // ISO date, misal "2026-08-30"
  to: string
}

export interface BestSellerItem {
  productId: string
  name: string
  qty: number
  revenue: number
}

export type StockStatus = 'AMAN' | 'MENIPIS' | 'HABIS'

export interface StockItem {
  productId: string
  name: string
  stock: number
  minimumStock: number
  stockStatus: StockStatus
}

export interface GrossProfitItem {
  period: string // label periode, misal "Sep W1", "Minggu 1"
  grossProfit: number
  margin: number // dalam persen, misal 24.5
}

export interface CashflowItem {
  period: string
  income: number
  expense: number
  net: number
}