import type { Transaction } from '../types/transaction'

export const mockSaleCash: Transaction = {
  id: '66f7a1000000000000000001',
  code: 'TRX-20260928-0001',
  type: 'SALE',
  status: 'COMPLETED',
  cashier: { id: '66f7a1000000000000000010', name: 'Siti Kasir' },
  customerName: 'Budi Santoso',
  member: { id: '66f7a1000000000000000020', memberNumber: 'KOP-001', name: 'Budi Santoso' },
  items: [
    { productId: 'p1', sku: 'ATK-001', name: 'Buku Tulis 38 Lembar', unit: 'pcs', quantity: 2, price: 4000, subtotal: 8000 },
    { productId: 'p2', sku: 'ATK-002', name: 'Pulpen', unit: 'pcs', quantity: 1, price: 2500, subtotal: 2500 },
  ],
  subtotal: 10500,
  discount: 0,
  tax: 0,
  total: 10500,
  payment: { method: 'CASH', amountPaid: 20000, change: 9500, paidAt: '2026-09-28T03:42:10Z' },
  notes: null,
  createdAt: '2026-09-28T03:42:10Z',
}

export const mockSaleQris: Transaction = {
  ...mockSaleCash,
  id: '66f7a1000000000000000002',
  code: 'TRX-20260928-0002',
  customerName: null,
  member: null,
  payment: { method: 'QRIS', amountPaid: 10500, change: 0, paidAt: '2026-09-28T04:10:00Z' },
  createdAt: '2026-09-28T04:10:00Z',
}