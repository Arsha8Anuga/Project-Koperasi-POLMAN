import type { SaleRequest } from '../types/sale'
import type { Transaction } from '../types/transaction'

const mockProducts = [
  { id: '1', sku: 'PRD-001', name: 'Kopi Susu Gula Aren', unit: 'Cup', sellingPrice: 18000 },
  { id: '2', sku: 'PRD-002', name: 'Roti Bakar Cokelat Keju', unit: 'Porsi', sellingPrice: 22000 },
  { id: '3', sku: 'PRD-003', name: 'Air Mineral 600ml', unit: 'Botol', sellingPrice: 5000 },
  { id: '4', sku: 'PRD-004', name: 'Kentang Goreng Original', unit: 'Porsi', sellingPrice: 15000 },
]

let counter = 3

// Menyimpan transaksi yang baru dibuat selama aplikasi berjalan (mock, hilang saat refresh)
export const createdSales: Transaction[] = []

export function mockCreateSale(req: SaleRequest): Promise<Transaction> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const items = []
      for (const line of req.items) {
        const p = mockProducts.find((x) => x.id === line.productId)
        if (!p) return reject(new Error('Produk tidak ditemukan'))
        items.push({
          productId: p.id, sku: p.sku, name: p.name, unit: p.unit,
          quantity: line.quantity, price: p.sellingPrice, subtotal: p.sellingPrice * line.quantity,
        })
      }
      const total = items.reduce((s, i) => s + i.subtotal, 0)

      let amountPaid = total
      if (req.payment.method === 'CASH') {
        amountPaid = req.payment.amountPaid ?? 0
        if (amountPaid < total) return reject(new Error('Uang yang diterima kurang dari total'))
      }

      const now = new Date().toISOString()
      const tx: Transaction = {
        id: `mock-${counter}`,
        code: `TRX-20260928-${String(counter++).padStart(4, '0')}`,
        type: 'SALE',
        status: 'COMPLETED',
        cashier: { id: 'u1', name: 'Siti Kasir' },
        customerName: req.customerName,
        member: req.memberId
          ? { id: req.memberId, memberNumber: '-', name: req.customerName ?? 'Anggota' }
          : null,
        items,
        subtotal: total, discount: 0, tax: 0, total,
        payment: { method: req.payment.method, amountPaid, change: amountPaid - total, paidAt: now },
        notes: null,
        createdAt: now,
      }

      createdSales.push(tx) // simpan supaya bisa dicari lagi lewat getById
      resolve(tx)
    }, 600)
  })
}