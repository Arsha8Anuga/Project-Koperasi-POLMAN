<script setup lang="ts">
import {
  ArrowRightLeftIcon,
  BoxesIcon,
  ChartColumnIcon,
  CircleAlertIcon,
  IdCardIcon,
  PackagePlusIcon,
  PackageXIcon,
  ScrollTextIcon,
  ShoppingCartIcon,
  TrendingUpIcon,
  TriangleAlertIcon,
  TruckIcon,
  UsersIcon,
  WalletIcon,
} from '@lucide/vue'
import { computed, onMounted, ref, type Component } from 'vue'
import PageHeader from '@/components/common/PageHeader.vue'
import StatCard from '@/components/common/StatCard.vue'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { dashboardApi } from '@/services/api'
import { errorMessage } from '@/services/apiClient'
import { useAuthStore } from '@/stores/auth'
import type { AdminSummary, LogistikSummary, OwnerSummary } from '@/types/api'
import { formatNumber, formatRupiah } from '@/utils/format'

type Tone = 'primary' | 'success' | 'warning' | 'danger' | 'neutral'
interface StatItem {
  label: string
  value: string
  icon: Component
  tone: Tone
  hint?: string
}

const auth = useAuthStore()
const summary = ref<OwnerSummary | LogistikSummary | AdminSummary | null>(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    summary.value = await dashboardApi.summary()
  } catch (e) {
    error.value = errorMessage(e, 'Gagal memuat ringkasan')
  } finally {
    loading.value = false
  }
})

const cards = computed<StatItem[]>(() => {
  const s = summary.value
  if (!s) return []
  if ('salesToday' in s)
    return [
      { label: 'Penjualan hari ini', value: formatRupiah(s.salesToday), icon: WalletIcon, tone: 'primary' },
      { label: 'Transaksi hari ini', value: formatNumber(s.transactionsToday), icon: ShoppingCartIcon, tone: 'neutral' },
      { label: 'Laba kotor hari ini', value: formatRupiah(s.grossProfitToday), icon: TrendingUpIcon, tone: 'success' },
      { label: 'Belanja restock hari ini', value: formatRupiah(s.restockToday), icon: PackagePlusIcon, tone: 'warning' },
    ]
  if ('activeProducts' in s)
    return [
      { label: 'Produk aktif', value: formatNumber(s.activeProducts), icon: BoxesIcon, tone: 'primary' },
      { label: 'Stok menipis', value: formatNumber(s.lowStockCount), icon: TriangleAlertIcon, tone: 'warning', hint: 'stok ≤ minimum' },
      { label: 'Stok habis', value: formatNumber(s.outOfStockCount), icon: PackageXIcon, tone: 'danger' },
      { label: 'Restock bulan ini', value: formatNumber(s.restocksThisMonth), icon: TruckIcon, tone: 'neutral' },
    ]
  return [
    { label: 'Pengguna aktif', value: formatNumber(s.activeUsers), icon: UsersIcon, tone: 'primary' },
    { label: 'Anggota aktif', value: formatNumber(s.activeMembers), icon: IdCardIcon, tone: 'success' },
    { label: 'Aktivitas hari ini', value: formatNumber(s.auditLogsToday), icon: ScrollTextIcon, tone: 'neutral', hint: 'entri audit trail' },
  ]
})

const usersByRole = computed(() => {
  const s = summary.value
  return s && 'usersByRole' in s ? Object.entries(s.usersByRole) : []
})

const shortcuts = computed(() => {
  const role = auth.user?.role
  if (role === 'OWNER')
    return [
      { to: { name: 'owner-transactions' }, label: 'Riwayat transaksi', icon: ArrowRightLeftIcon },
      { to: { name: 'owner-reports' }, label: 'Laporan & grafik', icon: ChartColumnIcon },
      { to: { name: 'stock' }, label: 'Pantau stok', icon: BoxesIcon },
    ]
  if (role === 'LOGISTIK')
    return [
      { to: { name: 'restock-new' }, label: 'Catat restock', icon: PackagePlusIcon },
      { to: { name: 'stock' }, label: 'Stok menipis', icon: TriangleAlertIcon },
      { to: { name: 'product-new' }, label: 'Tambah produk', icon: BoxesIcon },
    ]
  return [
    { to: { name: 'users' }, label: 'Kelola pengguna', icon: UsersIcon },
    { to: { name: 'members' }, label: 'Anggota koperasi', icon: IdCardIcon },
    { to: { name: 'audit-logs' }, label: 'Audit trail', icon: ScrollTextIcon },
  ]
})

const greeting = computed(() => {
  const h = Number(new Intl.DateTimeFormat('en-GB', { hour: 'numeric', timeZone: 'Asia/Jakarta' }).format(new Date()))
  return h < 11 ? 'Selamat pagi' : h < 15 ? 'Selamat siang' : h < 18 ? 'Selamat sore' : 'Selamat malam'
})
</script>

<template>
  <PageHeader :title="`${greeting}, ${auth.user?.name?.split(' ')[0] ?? ''}`" subtitle="Ringkasan hari ini (WIB)." />

  <Alert v-if="error" variant="destructive" class="mb-6">
    <CircleAlertIcon />
    <AlertDescription>{{ error }}</AlertDescription>
  </Alert>

  <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
    <template v-if="loading">
      <Skeleton v-for="n in 4" :key="n" class="h-[98px] rounded-xl" />
    </template>
    <StatCard v-for="c in cards" v-else :key="c.label" v-bind="c" />
  </div>

  <div class="mt-6 grid gap-6 lg:grid-cols-3">
    <Card class="lg:col-span-2">
      <CardHeader><CardTitle class="text-base">Pintasan</CardTitle></CardHeader>
      <CardContent class="grid gap-3 sm:grid-cols-3">
        <RouterLink
          v-for="s in shortcuts"
          :key="s.label"
          :to="s.to"
          class="group flex items-center gap-3 rounded-lg border bg-muted/40 p-4 transition outline-none hover:border-ring/50 hover:bg-accent focus-visible:ring-3 focus-visible:ring-ring/50"
        >
          <span class="flex size-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <component :is="s.icon" class="size-[19px]" />
          </span>
          <span class="text-sm font-semibold">{{ s.label }}</span>
        </RouterLink>
      </CardContent>
    </Card>

    <Card v-if="usersByRole.length">
      <CardHeader><CardTitle class="text-base">Pengguna per peran</CardTitle></CardHeader>
      <CardContent>
        <ul class="space-y-3">
          <li v-for="[role, n] in usersByRole" :key="role" class="flex items-center justify-between">
            <Badge variant="soft">{{ role }}</Badge>
            <span class="num font-bold">{{ n }}</span>
          </li>
        </ul>
      </CardContent>
    </Card>
  </div>
</template>
