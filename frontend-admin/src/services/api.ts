/**
 * Semua pemanggil API admin di satu tempat, dikelompokkan per modul (dokumen 04 §7).
 * Setiap fungsi melempar ApiException kalau gagal.
 */
import { api, clean } from './apiClient'
import type {
  AdminSummary,
  ApiResponse,
  AuditLog,
  BestSellerReport,
  CashflowReport,
  Category,
  GrossProfitReport,
  LogistikSummary,
  Member,
  MemberCreate,
  MemberUpdate,
  OwnerSummary,
  PageQuery,
  Paginated,
  Product,
  ProductInput,
  ReportPeriod,
  RestockInput,
  Role,
  StockMovement,
  StockReport,
  StockStatus,
  Supplier,
  SupplierInput,
  Transaction,
  TransactionPage,
  TransactionType,
  User,
  UserCreate,
} from '@/types/api'

const data = <T>(p: Promise<{ data: ApiResponse<T> }>) => p.then((r) => r.data.data)
const page = <T>(p: Promise<{ data: T }>) => p.then((r) => r.data)

export const dashboardApi = {
  summary: () => data<OwnerSummary | LogistikSummary | AdminSummary>(api.get('/dashboard/summary')),
}

export const userApi = {
  list: (q: PageQuery & { search?: string; role?: Role | ''; isActive?: boolean | '' }) =>
    page<Paginated<User>>(api.get('/users', { params: clean(q) })),
  create: (body: UserCreate) => data<User>(api.post('/users', body)),
  update: (id: string, body: { name: string; role: Role }) => data<User>(api.put(`/users/${id}`, body)),
  setStatus: (id: string, isActive: boolean) => data<User>(api.patch(`/users/${id}/status`, { isActive })),
  resetPassword: (id: string, newPassword: string) => data<null>(api.post(`/users/${id}/reset-password`, { newPassword })),
}

export const memberApi = {
  list: (q: PageQuery & { search?: string; isActive?: boolean | '' }) =>
    page<Paginated<Member>>(api.get('/members', { params: clean(q) })),
  create: (body: MemberCreate) => data<Member>(api.post('/members', body)),
  update: (id: string, body: MemberUpdate) => data<Member>(api.put(`/members/${id}`, body)),
}

export const auditApi = {
  list: (
    q: PageQuery & { userId?: string; module?: string; action?: string; from?: string; to?: string },
  ) => page<Paginated<AuditLog>>(api.get('/audit-logs', { params: clean(q) })),
}

export const categoryApi = {
  list: (isActive?: boolean) => data<Category[]>(api.get('/categories', { params: clean({ isActive }) })),
  create: (body: { name: string; description: string | null }) => data<Category>(api.post('/categories', body)),
  update: (id: string, body: { name: string; description: string | null; isActive: boolean }) =>
    data<Category>(api.put(`/categories/${id}`, body)),
}

export const productApi = {
  list: (
    q: PageQuery & {
      search?: string
      categoryId?: string
      isActive?: boolean | ''
      stockStatus?: StockStatus | ''
      sort?: 'name' | 'stock' | '-stock' | '-createdAt'
    },
  ) => page<Paginated<Product>>(api.get('/products', { params: clean(q) })),
  get: (id: string) => data<Product>(api.get(`/products/${id}`)),
  create: (body: ProductInput) => data<Product>(api.post('/products', body)),
  update: (id: string, body: ProductInput) => data<Product>(api.put(`/products/${id}`, body)),
  setStatus: (id: string, isActive: boolean) => data<Product>(api.patch(`/products/${id}/status`, { isActive })),
}

export const supplierApi = {
  list: (q: PageQuery & { search?: string; isActive?: boolean | '' }) =>
    page<Paginated<Supplier>>(api.get('/suppliers', { params: clean(q) })),
  create: (body: SupplierInput) => data<Supplier>(api.post('/suppliers', body)),
  update: (id: string, body: SupplierInput) => data<Supplier>(api.put(`/suppliers/${id}`, body)),
  setStatus: (id: string, isActive: boolean) => data<Supplier>(api.patch(`/suppliers/${id}/status`, { isActive })),
}

export const restockApi = {
  list: (q: PageQuery & { supplierId?: string; from?: string; to?: string }) =>
    page<Paginated<Transaction>>(api.get('/restocks', { params: clean(q) })),
  get: (id: string) => data<Transaction>(api.get(`/restocks/${id}`)),
  create: (body: RestockInput) => data<Transaction>(api.post('/restocks', body)),
}

export const transactionApi = {
  list: (
    q: PageQuery & { type?: TransactionType | ''; from?: string; to?: string; search?: string; sort?: string },
  ) => page<TransactionPage>(api.get('/transactions', { params: clean(q) })),
  get: (id: string) => data<Transaction>(api.get(`/transactions/${id}`)),
}

export const stockApi = {
  movements: (q: PageQuery & { productId?: string; type?: string; from?: string; to?: string }) =>
    page<Paginated<StockMovement>>(api.get('/stock/movements', { params: clean(q) })),
  report: (q: { categoryId?: string; stockStatus?: StockStatus | '' }) =>
    data<StockReport>(api.get('/reports/stock', { params: clean(q) })),
}

export const reportApi = {
  cashflow: (p: ReportPeriod) => data<CashflowReport>(api.get('/reports/cashflow', { params: p })),
  grossProfit: (p: ReportPeriod) => data<GrossProfitReport>(api.get('/reports/gross-profit', { params: p })),
  bestSellers: (p: { from: string; to: string; limit?: number; categoryId?: string }) =>
    data<BestSellerReport>(api.get('/reports/best-sellers', { params: clean(p) })),
}
