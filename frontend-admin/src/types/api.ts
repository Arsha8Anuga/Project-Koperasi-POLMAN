/** Tipe data = kontrak API dokumen 04 §4–§7. Kalau backend berubah, ubah di sini dulu. */

export type Role = 'OWNER' | 'LOGISTIK' | 'ADMIN' | 'KASIR'
export type StockStatus = 'OK' | 'LOW' | 'OUT'
export type PaymentMethod = 'CASH' | 'QRIS'
export type TransactionType = 'SALE' | 'RESTOCK'
export type Granularity = 'day' | 'week' | 'month' | 'year'
export type AuditAction =
  | 'LOGIN'
  | 'LOGOUT'
  | 'CREATE'
  | 'UPDATE'
  | 'DEACTIVATE'
  | 'ACTIVATE'
  | 'RESET_PASSWORD'
  | 'SALE'
  | 'RESTOCK'
export type AuditModule = 'AUTH' | 'USER' | 'MEMBER' | 'CATEGORY' | 'PRODUCT' | 'SUPPLIER' | 'RESTOCK' | 'SALE'

export interface ApiResponse<T> {
  success: true
  message: string
  data: T
}

export interface PageMeta {
  page: number
  limit: number
  total: number
  totalPages: number
}

export interface Paginated<T> extends ApiResponse<T[]> {
  meta: PageMeta
}

export interface PageQuery {
  page?: number
  limit?: number
}

// ---------- Auth & User ----------
export interface User {
  id: string
  name: string
  username: string
  role: Role
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface LoginData {
  token: string
  expiresAt: string
  user: Pick<User, 'id' | 'name' | 'username' | 'role'>
}

export interface UserCreate {
  name: string
  username: string
  password: string
  role: Role
}

// ---------- Member ----------
export interface Member {
  id: string
  memberNumber: string
  name: string
  phone: string | null
  isActive: boolean
  joinedAt: string
  createdAt: string
  updatedAt: string
}

export interface MemberCreate {
  memberNumber: string
  name: string
  phone: string | null
  joinedAt?: string
}

export interface MemberUpdate {
  name: string
  phone: string | null
  isActive: boolean
}

// ---------- Katalog ----------
export interface Category {
  id: string
  name: string
  description: string | null
  isActive: boolean
}

export interface Product {
  id: string
  sku: string
  barcode: string | null
  name: string
  categoryId: string
  categoryName: string | null
  unit: string
  sellingPrice: number
  costPrice: number
  lastPurchasePrice: number
  stock: number
  minimumStock: number
  stockStatus: StockStatus
  imageUrl: string | null
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface ProductInput {
  sku: string
  barcode: string | null
  name: string
  categoryId: string
  unit: string
  sellingPrice: number
  minimumStock: number
  imageUrl: string | null
}

export interface Supplier {
  id: string
  supplierCode: string
  name: string
  contactPerson: string | null
  phone: string | null
  email: string | null
  address: string | null
  notes: string | null
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export type SupplierInput = Omit<Supplier, 'id' | 'isActive' | 'createdAt' | 'updatedAt'>

// ---------- Transaksi ----------
export interface Actor {
  id: string
  name: string
}

export interface TransactionItem {
  productId: string
  sku: string
  name: string
  unit: string
  quantity: number
  price?: number
  costPrice?: number
  purchasePrice?: number
  subtotal: number
}

export interface Transaction {
  id: string
  code: string
  type: TransactionType
  status: 'COMPLETED'
  cashier: Actor | null
  customerName: string | null
  member: { id: string; memberNumber: string; name: string } | null
  supplier: { id: string; supplierCode: string; name: string } | null
  items: TransactionItem[]
  subtotal: number
  discount: number
  tax: number
  total: number
  payment: { method: PaymentMethod; amountPaid: number; change: number; paidAt: string } | null
  notes: string | null
  createdBy: Actor
  createdAt: string
}

export interface TransactionSummary {
  count: number
  totalSales: number
  totalRestock: number
}

export interface TransactionPage extends Paginated<Transaction> {
  summary: TransactionSummary
}

export interface RestockInput {
  supplierId: string
  items: { productId: string; quantity: number; purchasePrice: number }[]
  notes: string | null
}

// ---------- Stok ----------
export interface StockMovement {
  id: string
  productId: string
  productName: string
  type: 'SALE' | 'RESTOCK' | 'ADJUSTMENT'
  quantity: number
  stockBefore: number
  stockAfter: number
  referenceCode: string
  referenceId: string
  createdBy: Actor
  createdAt: string
}

export interface StockReportItem {
  productId: string
  sku: string
  name: string
  categoryName: string | null
  stock: number
  minimumStock: number
  stockStatus: StockStatus
}

export interface StockReport {
  items: StockReportItem[]
  counts: Record<StockStatus, number>
}

// ---------- Laporan ----------
export interface CashflowBucket {
  period: string
  income: number
  expense: number
  net: number
}

export interface CashflowReport {
  granularity: Granularity
  from: string
  to: string
  buckets: CashflowBucket[]
  totals: { income: number; expense: number; net: number }
}

export interface GrossProfitBucket {
  period: string
  revenue: number
  cogs: number
  grossProfit: number
  margin: number
}

export interface GrossProfitReport {
  granularity: Granularity
  from: string
  to: string
  buckets: GrossProfitBucket[]
  totals: { revenue: number; cogs: number; grossProfit: number; margin: number }
}

export interface BestSellerReport {
  from: string
  to: string
  items: { rank: number; productId: string; sku: string; name: string; quantitySold: number; revenue: number }[]
}

export interface ReportPeriod {
  granularity: Granularity
  from: string
  to: string
}

// ---------- Audit & Dashboard ----------
export interface AuditLog {
  id: string
  user: { id: string; name: string; role: Role }
  action: AuditAction
  module: AuditModule
  referenceId: string | null
  description: string
  ip: string | null
  createdAt: string
}

export interface OwnerSummary {
  salesToday: number
  transactionsToday: number
  grossProfitToday: number
  restockToday: number
}

export interface LogistikSummary {
  activeProducts: number
  lowStockCount: number
  outOfStockCount: number
  restocksThisMonth: number
}

export interface AdminSummary {
  activeUsers: number
  usersByRole: Record<string, number>
  activeMembers: number
  auditLogsToday: number
}
