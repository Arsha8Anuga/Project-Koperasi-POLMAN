import type { SaleRequest } from '../types/sale'
import type { Transaction } from '../types/transaction'
import type { Paginated } from '../types/api'
import { mockCreateSale, createdSales } from '../mocks/checkout'
import { mockListMySales } from '../mocks/history'
// import api from './api'

export const salesApi = {
  create: (req: SaleRequest): Promise<Transaction> => {
    return mockCreateSale(req)
    // nanti: return api.post<{ data: Transaction }>('/sales', req).then((r) => r.data.data)
  },

  mine: (page: number, limit: number): Promise<Paginated<Transaction>> => {
    return mockListMySales(page, limit).then((res) => {
      // taruh transaksi baru (createdSales) di paling atas, hanya di halaman 1
      if (page === 1 && createdSales.length > 0) {
        const merged = [...createdSales].reverse().concat(res.data).slice(0, limit)
        return {
          ...res,
          data: merged,
          meta: { ...res.meta, total: res.meta.total + createdSales.length },
        }
      }
      return res
    })
    // nanti: return api.get<Paginated<Transaction>>('/sales/mine', { params: { page, limit } }).then((r) => r.data)
  },

  getById: (id: string): Promise<Transaction> => {
    return new Promise((resolve, reject) => {
      const fromNew = createdSales.find((tx) => tx.id === id)
      if (fromNew) return resolve(fromNew)

      mockListMySales(1, 100).then((res) => {
        const found = res.data.find((tx) => tx.id === id)
        if (found) resolve(found)
        else reject(new Error('Transaksi tidak ditemukan'))
      })
    })
    // nanti: return api.get<{ data: Transaction }>(`/sales/${id}`).then((r) => r.data.data)
  },
}