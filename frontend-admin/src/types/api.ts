export type Role = 'OWNER' | 'LOGISTIK' | 'ADMIN' | 'KASIR'

export interface ApiResponse<T> {
  success: true
  message: string
  data: T
}

export interface Paginated<T> extends ApiResponse<T[]> {
  meta: { page: number; limit: number; total: number; totalPages: number }
}

export interface ApiError {
  success: false
  message: string
  error: { code: string; details?: unknown[] }
}

// TODO: samakan dengan dokumen 04
export interface User {
  id: string
  name: string
  username: string
  role: Role
}

// TODO: samakan persis dengan dokumen 04 §5
export interface Category {
  id: string
  name: string
}

export interface Product {
  id: string
  sku: string
  name: string
  categoryId: string
  categoryName?: string
  sellPrice: number
  costPrice?: number
  lastPurchasePrice?: number
  stock: number
  minimumStock: number
  isActive: boolean
  stockStatus: 'AMAN' | 'MENIPIS' | 'HABIS'
}

export interface ProductQuery {
  page: number
  limit: number
  search?: string
}

// TODO: samakan persis dengan dokumen 04 §5
export interface Supplier {
  id: string
  name: string
  phone?: string
  address?: string
}

// TODO: samakan persis dengan dokumen 04/05
export interface RestockItem {
  productId: string
  productName: string
  qty: number
  purchasePrice: number
}

export interface Restock {
  id: string
  code: string
  supplierId: string
  supplierName: string
  note?: string
  items: RestockItem[]
  total: number
  createdAt: string
}

export interface RestockInput {
  supplierId: string
  note?: string
  items: { productId: string; qty: number; purchasePrice: number }[]
}
// TODO: samakan persis dengan dokumen 04 §5
export interface AdminUser {
  id: string
  name: string
  username: string
  role: Role
  isActive: boolean
}

export interface AdminUserInput {
  name: string
  username: string
  role: Role
  password?: string
}
// TODO: samakan persis dengan dokumen 04 §5
export interface Member {
  id: string
  memberNumber: string
  name: string
  phone?: string
  isActive: boolean
}

export interface MemberInput {
  memberNumber: string
  name: string
  phone?: string
}
// TODO: samakan persis dengan dokumen 04/05
export interface AuditLog {
  id: string
  userName: string
  userRole: Role
  action: string
  entity: string
  detail?: string
  createdAt: string
}
// TODO: samakan persis dengan dokumen 04/05
export interface TransactionItem {
  productName: string
  qty: number
  price: number
  subtotal: number
}

export interface Transaction {
  id: string
  code: string
  type: 'SALE' | 'RESTOCK'
  cashierName?: string
  supplierName?: string
  items: TransactionItem[]
  total: number
  paymentMethod?: 'CASH' | 'QRIS'
  amountPaid?: number
  change?: number
  createdAt: string
}

export interface TransactionQuery {
  from?: string
  to?: string
  type?: 'SALE' | 'RESTOCK'
}
// TODO: samakan persis dengan dokumen 04/05 (bentuk per role kemungkinan beda)
export interface DashboardSummary {
  // OWNER
  todaySales?: number
  todayTransactionCount?: number
  grossProfitThisMonth?: number
  // LOGISTIK
  lowStockCount?: number
  outOfStockCount?: number
  pendingRestockCount?: number
  // ADMIN
  totalUsers?: number
  totalMembers?: number
  todayAuditCount?: number
}