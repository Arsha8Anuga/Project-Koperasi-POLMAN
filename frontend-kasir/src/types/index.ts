/** Tipe data = kontrak API dokumen 04. Kalau backend berubah, ubah di sini dulu. */

export type Role = 'OWNER' | 'LOGISTIK' | 'ADMIN' | 'KASIR'
export type StockStatus = 'OK' | 'LOW' | 'OUT'
export type PaymentMethod = 'CASH' | 'QRIS'

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

export interface UserBrief {
  id: string
  name: string
  username: string
  role: Role
}

export interface LoginData {
  token: string
  expiresAt: string
  user: UserBrief
}

export interface Category {
  id: string
  name: string
  description: string | null
  isActive: boolean
}

/** Product versi KASIR: backend tidak mengirim costPrice & lastPurchasePrice. */
export interface Product {
  id: string
  sku: string
  barcode: string | null
  name: string
  categoryId: string
  categoryName: string | null
  unit: string
  sellingPrice: number
  stock: number
  minimumStock: number
  stockStatus: StockStatus
  imageUrl: string | null
  isActive: boolean
}

export interface MemberLookup {
  id: string
  memberNumber: string
  name: string
}

/** Pendaftaran anggota oleh kasir. Nomor anggota dibuat backend (KOP-NNN). */
export interface MemberCreate {
  name: string
  phone: string | null
}

export interface Member extends MemberLookup {
  phone: string | null
  isActive: boolean
  joinedAt: string
}

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

export interface Sale {
  id: string
  code: string
  type: 'SALE'
  status: 'COMPLETED'
  cashier: { id: string; name: string }
  customerName: string | null
  member: MemberLookup | null
  items: SaleItem[]
  subtotal: number
  discount: number
  tax: number
  total: number
  payment: Payment
  notes: string | null
  createdAt: string
}

export interface SaleRequest {
  items: { productId: string; quantity: number }[]
  customerName: string | null
  memberId: string | null
  payment: { method: 'CASH'; amountPaid: number } | { method: 'QRIS' }
}

export interface CartItem {
  productId: string
  sku: string
  name: string
  unit: string
  price: number
  quantity: number
  stock: number
  /** Untuk thumbnail di detail pesanan (item lama di localStorage bisa belum punya). */
  imageUrl?: string | null
}

/** Detail error INSUFFICIENT_STOCK / PRODUCT_INACTIVE dari backend. */
export interface StockIssue {
  field?: string
  productId?: string
  name?: string
  requested?: number
  available?: number
}

/** Bagian produk yang dibutuhkan keranjang (produk katalog atau saran AI). */
export type CartProduct = Pick<Product, 'id' | 'sku' | 'name' | 'unit' | 'sellingPrice' | 'stock'> & { imageUrl?: string | null }

/** Saran "sering dibeli bersama" dari AI engine (GET /insights/frequently-bought). */
export interface Suggestion {
  product: CartProduct
  because: string[]
  confidence: number
  lift: number
}
