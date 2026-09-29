import type { PaymentMethod } from './transaction'

export interface SaleRequest {
  items: { productId: string; quantity: number }[]
  customerName: string | null
  memberId: string | null
  payment: { method: PaymentMethod; amountPaid?: number }
}