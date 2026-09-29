import type { ReportParams, BestSellerItem, StockItem, GrossProfitItem, CashflowItem } from '../types/report'
import { mockGetBestSellers, mockGetStockReport, mockGetGrossProfit, mockGetCashflow } from '../mocks/reports'
// import { api } from './api'

export const reportsApi = {
  bestSellers: (_params: ReportParams): Promise<BestSellerItem[]> => {
    return mockGetBestSellers()
    // nanti: return api.get('/reports/best-sellers', { params: _params }).then((r) => r.data.data)
  },
  stock: (_params: ReportParams): Promise<StockItem[]> => {
    return mockGetStockReport()
    // nanti: return api.get('/reports/stock', { params: _params }).then((r) => r.data.data)
  },
  grossProfit: (_params: ReportParams): Promise<GrossProfitItem[]> => {
    return mockGetGrossProfit()
    // nanti: return api.get('/reports/gross-profit', { params: _params }).then((r) => r.data.data)
  },
  cashflow: (_params: ReportParams): Promise<CashflowItem[]> => {
    return mockGetCashflow()
    // nanti: return api.get('/reports/cashflow', { params: _params }).then((r) => r.data.data)
  },
}