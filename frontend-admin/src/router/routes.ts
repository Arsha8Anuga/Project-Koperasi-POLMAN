import type { RouteRecordRaw } from 'vue-router'
import type { Role } from '@/types/api'

declare module 'vue-router' {
  interface RouteMeta {
    public?: boolean
    roles?: Role[]
    title?: string
    menu?: { label: string; group: string }
  }
}

const Placeholder = () => import('@/pages/PlaceholderPage.vue')

export const appRoutes: RouteRecordRaw[] = [
  { path: '', name: 'dashboard', component: () => import('@/pages/dashboard/DashboardPage.vue'),
  meta: { title: 'Dashboard', menu: { label: 'Dashboard', group: 'Umum' } } },

  { path: '/owner/transactions', name: 'owner-transactions', component: () => import('@/pages/owner/TransactionsPage.vue'),
  meta: { title: 'Riwayat Transaksi', roles: ['OWNER'], menu: { label: 'Transaksi', group: 'Owner' } } },
  { path: '/owner/transactions/:id', name: 'owner-transactions-detail', component: () => import('@/pages/owner/TransactionDetailPage.vue'),
  meta: { title: 'Detail Transaksi', roles: ['OWNER'] } },
  { path: '/owner/reports', name: 'owner-reports', component: Placeholder,
    meta: { title: 'Laporan', roles: ['OWNER'], menu: { label: 'Laporan', group: 'Owner' } } },

  { path: '/logistik/products', name: 'logistik-products', component: () => import('@/pages/logistik/ProductsPage.vue'),
    meta: { title: 'Produk', roles: ['LOGISTIK'], menu: { label: 'Produk', group: 'Logistik' } } },
  { path: '/logistik/products/new', name: 'logistik-products-new', component: () => import('@/pages/logistik/ProductFormPage.vue'),
    meta: { title: 'Produk Baru', roles: ['LOGISTIK'] } },
  { path: '/logistik/products/:id', name: 'logistik-products-edit', component: () => import('@/pages/logistik/ProductFormPage.vue'),
    meta: { title: 'Ubah Produk', roles: ['LOGISTIK'] } },

  { path: '/logistik/categories', name: 'logistik-categories', component: () => import('@/pages/logistik/CategoriesPage.vue'),
  meta: { title: 'Kategori', roles: ['LOGISTIK'], menu: { label: 'Kategori', group: 'Logistik' } } },
  { path: '/logistik/suppliers', name: 'logistik-suppliers', component: () => import('@/pages/logistik/SuppliersPage.vue'),
  meta: { title: 'Supplier', roles: ['LOGISTIK'], menu: { label: 'Supplier', group: 'Logistik' } } },
  { path: '/logistik/restocks', name: 'logistik-restocks', component: () => import('@/pages/logistik/RestocksPage.vue'),
  meta: { title: 'Restock', roles: ['LOGISTIK'], menu: { label: 'Restock', group: 'Logistik' } } },
  { path: '/logistik/restocks/new', name: 'logistik-restocks-new', component: () => import('@/pages/logistik/RestockFormPage.vue'),
  meta: { title: 'Restock Baru', roles: ['LOGISTIK'] } },
  { path: '/logistik/stock', name: 'logistik-stock', component: Placeholder,
    meta: { title: 'Stok', roles: ['LOGISTIK'], menu: { label: 'Stok', group: 'Logistik' } } },

  { path: '/admin/users', name: 'admin-users', component: () => import('@/pages/admin/UsersPage.vue'),
  meta: { title: 'User', roles: ['ADMIN'], menu: { label: 'User', group: 'Admin' } } },
  { path: '/admin/members', name: 'admin-members', component: () => import('@/pages/admin/MembersPage.vue'),
  meta: { title: 'Anggota Koperasi', roles: ['ADMIN'], menu: { label: 'Anggota', group: 'Admin' } } },
  { path: '/admin/audit-logs', name: 'admin-audit-logs', component: () => import('@/pages/admin/AuditLogsPage.vue'),
  meta: { title: 'Audit Trail', roles: ['ADMIN'], menu: { label: 'Audit Trail', group: 'Admin' } } },
]