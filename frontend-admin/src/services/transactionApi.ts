import { api } from './apiClient'
import type { Transaction, TransactionQuery } from '@/types/api'

const MOCK = import.meta.env.VITE_MOCK_AUTH === 'true'

const mockTransactions: Transaction[] = [
  {
    id: 't1', code: 'TRX-20260928-0001', type: 'SALE', cashierName: 'Siti Aminah',
    items: [
      { productName: 'Buku Tulis', qty: 2, price: 4000, subtotal: 8000 },
      { productName: 'Pulpen', qty: 1, price: 2500, subtotal: 2500 },
    ],
    total: 10500, paymentMethod: 'CASH', amountPaid: 20000, change: 9500,
    createdAt: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: 't2', code: 'TRX-20260928-0002', type: 'SALE', cashierName: 'Siti Aminah',
    items: [{ productName: 'Indomie Goreng', qty: 5, price: 3500, subtotal: 17500 }],
    total: 17500, paymentMethod: 'QRIS', createdAt: new Date(Date.now() - 7200000).toISOString(),
  },
]

export const transactionApi = {
  async list(q: TransactionQuery): Promise<Transaction[]> {
    if (MOCK) {
      return mockTransactions.filter((t) => (q.type ? t.type === q.type : true))
    }
    // TODO: cek nama query param di dokumen 04
    const res = await api.get<{ success: true; message: string; data: Transaction[] }>('/transactions', { params: q })
    return res.data.data
  },

  async get(id: string): Promise<Transaction> {
    if (MOCK) {
      const found = mockTransactions.find((t) => t.id === id)
      if (!found) throw new Error('Transaksi tidak ditemukan')
      return found
    }
    const res = await api.get<{ success: true; message: string; data: Transaction }>(`/transactions/${id}`)
    return res.data.data
  },
}