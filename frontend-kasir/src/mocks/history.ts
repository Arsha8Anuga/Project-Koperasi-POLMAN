import type { Paginated } from '../types/api'
import type { Transaction } from '../types/transaction'
import { mockSaleCash } from './sales'

const allSales: Transaction[] = Array.from({ length: 25 }, (_, i) => {
  const n = 25 - i // yang terbaru di atas
  const isQris = n % 3 === 0
  const total = mockSaleCash.total + (n % 5) * 1000
  const createdAt = new Date(Date.UTC(2026, 8, 28, 8, 0) - i * 20 * 60 * 1000).toISOString()
  return {
    ...mockSaleCash,
    id: `mock-h-${n}`,
    code: `TRX-20260928-${String(n).padStart(4, '0')}`,
    total,
    subtotal: total,
    member: n % 4 === 0 ? mockSaleCash.member : null,
    customerName: n % 4 === 0 ? mockSaleCash.customerName : null,
    payment: {
      method: isQris ? 'QRIS' : 'CASH',
      amountPaid: isQris ? total : total + 5000,
      change: isQris ? 0 : 5000,
      paidAt: createdAt,
    },
    createdAt,
  }
})

// Meniru GET /sales/mine?page=&limit=
export function mockListMySales(page: number, limit: number): Promise<Paginated<Transaction>> {
  return new Promise((resolve) => {
    setTimeout(() => {
      const start = (page - 1) * limit
      resolve({
        success: true,
        message: 'OK',
        data: allSales.slice(start, start + limit),
        meta: { page, limit, total: allSales.length, totalPages: Math.ceil(allSales.length / limit) },
      })
    }, 400)
  })
}