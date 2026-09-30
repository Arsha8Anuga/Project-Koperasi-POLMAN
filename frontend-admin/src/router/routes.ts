import {
  ArrowRightLeftIcon,
  BoxesIcon,
  ChartColumnIcon,
  IdCardIcon,
  LayoutDashboardIcon,
  PackageIcon,
  PackagePlusIcon,
  ScrollTextIcon,
  SparklesIcon,
  TagsIcon,
  TruckIcon,
  UsersIcon,
} from '@lucide/vue'
import type { RouteRecordRaw } from 'vue-router'

/**
 * Semua halaman di dalam layout dashboard. `meta.roles` = siapa yang boleh membuka
 * (dicek guard); `meta.menu` = muncul di sidebar (difilter per role).
 * Menyembunyikan menu BUKAN keamanan — backend tetap menolak dengan 403.
 */
export const appRoutes: RouteRecordRaw[] = [
  {
    path: '',
    name: 'dashboard',
    component: () => import('@/pages/dashboard/DashboardPage.vue'),
    meta: { title: 'Dashboard', menu: { label: 'Dashboard', group: 'Umum', icon: LayoutDashboardIcon } },
  },

  // OWNER
  {
    path: 'owner/transactions',
    name: 'owner-transactions',
    component: () => import('@/pages/owner/TransactionsPage.vue'),
    meta: { title: 'Riwayat Transaksi', roles: ['OWNER'], menu: { label: 'Transaksi', group: 'Owner', icon: ArrowRightLeftIcon } },
  },
  {
    path: 'owner/transactions/:id',
    name: 'owner-transaction-detail',
    component: () => import('@/pages/owner/TransactionDetailPage.vue'),
    meta: { title: 'Detail Transaksi', roles: ['OWNER'] },
  },
  {
    path: 'owner/reports',
    name: 'owner-reports',
    component: () => import('@/pages/owner/ReportsPage.vue'),
    meta: { title: 'Laporan', roles: ['OWNER'], menu: { label: 'Laporan', group: 'Owner', icon: ChartColumnIcon } },
  },

  // LOGISTIK
  {
    path: 'logistik/products',
    name: 'products',
    component: () => import('@/pages/logistik/ProductsPage.vue'),
    meta: { title: 'Produk', roles: ['LOGISTIK'], menu: { label: 'Produk', group: 'Logistik', icon: PackageIcon } },
  },
  {
    path: 'logistik/products/new',
    name: 'product-new',
    component: () => import('@/pages/logistik/ProductFormPage.vue'),
    meta: { title: 'Produk Baru', roles: ['LOGISTIK'] },
  },
  {
    path: 'logistik/products/:id',
    name: 'product-edit',
    component: () => import('@/pages/logistik/ProductFormPage.vue'),
    meta: { title: 'Ubah Produk', roles: ['LOGISTIK'] },
  },
  {
    path: 'logistik/categories',
    name: 'categories',
    component: () => import('@/pages/logistik/CategoriesPage.vue'),
    meta: { title: 'Kategori', roles: ['LOGISTIK'], menu: { label: 'Kategori', group: 'Logistik', icon: TagsIcon } },
  },
  {
    path: 'logistik/suppliers',
    name: 'suppliers',
    component: () => import('@/pages/logistik/SuppliersPage.vue'),
    meta: { title: 'Supplier', roles: ['LOGISTIK'], menu: { label: 'Supplier', group: 'Logistik', icon: TruckIcon } },
  },
  {
    path: 'logistik/restocks',
    name: 'restocks',
    component: () => import('@/pages/logistik/RestocksPage.vue'),
    meta: { title: 'Restock', roles: ['LOGISTIK'], menu: { label: 'Restock', group: 'Logistik', icon: PackagePlusIcon } },
  },
  {
    path: 'logistik/restocks/new',
    name: 'restock-new',
    component: () => import('@/pages/logistik/RestockFormPage.vue'),
    meta: { title: 'Restock Baru', roles: ['LOGISTIK'] },
  },
  {
    path: 'restocks/:id',
    name: 'restock-detail',
    component: () => import('@/pages/logistik/RestockDetailPage.vue'),
    meta: { title: 'Detail Restock', roles: ['LOGISTIK', 'OWNER'] },
  },
  {
    path: 'stock',
    name: 'stock',
    component: () => import('@/pages/logistik/StockPage.vue'),
    meta: { title: 'Stok', roles: ['LOGISTIK', 'OWNER'], menu: { label: 'Stok', group: 'Persediaan', icon: BoxesIcon } },
  },

  // ADMIN
  {
    path: 'admin/users',
    name: 'users',
    component: () => import('@/pages/admin/UsersPage.vue'),
    meta: { title: 'Pengguna', roles: ['ADMIN'], menu: { label: 'Pengguna', group: 'Admin', icon: UsersIcon } },
  },
  {
    path: 'admin/members',
    name: 'members',
    component: () => import('@/pages/admin/MembersPage.vue'),
    meta: { title: 'Anggota Koperasi', roles: ['ADMIN'], menu: { label: 'Anggota', group: 'Admin', icon: IdCardIcon } },
  },
  {
    path: 'admin/audit-logs',
    name: 'audit-logs',
    component: () => import('@/pages/admin/AuditLogsPage.vue'),
    meta: { title: 'Audit Trail', roles: ['ADMIN'], menu: { label: 'Audit Trail', group: 'Admin', icon: ScrollTextIcon } },
  },
  {
    path: 'admin/ai-engine',
    name: 'ai-engine',
    component: () => import('@/pages/admin/AiEnginePage.vue'),
    meta: { title: 'AI Engine', roles: ['ADMIN'], menu: { label: 'AI Engine', group: 'Admin', icon: SparklesIcon } },
  },
]
