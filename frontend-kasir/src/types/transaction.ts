export type PaymentMethod = 'CASH' | 'QRIS'

export interface SaleItem {
  productId: string
  sku: string
  name: string
  unit: string
  quantity: number
  price: number
  subtotal: number
}

export interface Payment {
  method: PaymentMethod
  amountPaid: number
  change: number
  paidAt: string
}

export interface Transaction {
  id: string
  code: string
  type: 'SALE'
  status: 'COMPLETED'
  cashier: { id: string; name: string }
  customerName: string | null
  member: { id: string; memberNumber: string; name: string } | null
  items: SaleItem[]
  subtotal: number
  discount: number
  tax: number
  total: number
  payment: Payment
  notes: string | null
  createdAt: string
}