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
import ChartCard from '@/components/charts/ChartCard.vue'
import BestSellerChart from '@/components/charts/BestSellerChart.vue'
import CashflowChart from '@/components/charts/CashflowChart.vue'
import StockoutRiskChart from '@/components/charts/StockoutRiskChart.vue'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { dashboardApi, insightApi, reportApi } from '@/services/api'
import { errorMessage } from '@/services/apiClient'
import { useAuthStore } from '@/stores/auth'
import type { AdminSummary, BestSellerReport, CashflowReport, ForecastList, LogistikSummary, OwnerSummary } from '@/types/api'
import { formatDateTime, formatNumber, formatRupiah, todayWib } from '@/utils/format'
import { useRouter } from 'vue-router'

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

// LOGISTIK: mini chart 5 produk yang paling cepat habis menurut AI engine (gagal = kartu disembunyikan)
const router = useRouter()
const forecast = ref<ForecastList | null>(null)
const forecastLoading = ref(false)
async function loadForecast() {
  forecastLoading.value = true
  try {
    forecast.value = await insightApi.forecast()
  } catch {
    forecast.value = null
  } finally {
    forecastLoading.value = false
  }
}
const urgent = computed(() => (forecast.value?.products ?? []).filter((p) => p.daysUntilStockout !== null))

// OWNER: tren harian 14 hari (arus kas: jumlah per hari → batang) + 5 produk terlaris 30 hari (peringkat → batang horizontal)
const cash = ref<CashflowReport | null>(null)
const best = ref<BestSellerReport | null>(null)
const ownerLoading = ref(false)
const ownerError = ref('')
async function loadOwnerCharts() {
  ownerLoading.value = true
  try {
    const [c, b] = await Promise.all([
      reportApi.cashflow({ granularity: 'day', from: todayWib(-13), to: todayWib() }),
      reportApi.bestSellers({ from: todayWib(-29), to: todayWib(), limit: 5 }),
    ])
    cash.value = c
    best.value = b
  } catch (e) {
    ownerError.value = errorMessage(e, 'Gagal memuat grafik')
  } finally {
    ownerLoading.value = false
  }
}
const cashEmpty = computed(() => !cash.value?.buckets.some((b) => b.income || b.expense))

// LOGISTIK: komposisi stok (bagian dari satu keseluruhan → satu batang bersegmen, bukan grafik terpisah)
const stockParts = computed(() => {
  const s = summary.value
  if (!s || !('activeProducts' in s)) return []
  const ok = Math.max(0, s.activeProducts - s.lowStockCount - s.outOfStockCount)
  return [
    { label: 'Aman', value: ok, bar: 'bg-success', dot: 'bg-success' },
    { label: 'Menipis', value: s.lowStockCount, bar: 'bg-warning', dot: 'bg-warning' },
    { label: 'Habis', value: s.outOfStockCount, bar: 'bg-destructive', dot: 'bg-destructive' },
  ]
})
const stockTotal = computed(() => stockParts.value.reduce((n, p) => n + p.value, 0))

onMounted(async () => {
  if (auth.user?.role === 'LOGISTIK') loadForecast()
  if (auth.user?.role === 'OWNER') loadOwnerCharts()
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

const ROLE_LABEL: Record<string, string> = { OWNER: 'Owner', LOGISTIK: 'Logistik', ADMIN: 'Admin', KASIR: 'Kasir' }
const usersByRole = computed(() => {
  const s = summary.value
  return s && 'usersByRole' in s ? Object.entries(s.usersByRole).sort((a, b) => b[1] - a[1]) : []
})
const maxRole = computed(() => Math.max(1, ...usersByRole.value.map(([, n]) => n)))

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

  <!-- OWNER -->
  <div v-if="auth.user?.role === 'OWNER'" class="mt-6 grid gap-6 xl:grid-cols-3">
    <ChartCard
      class="xl:col-span-2"
      title="Arus kas 14 hari terakhir"
      subtitle="Pemasukan penjualan dan belanja restock per hari"
      :loading="ownerLoading"
      :error="ownerError"
      :empty="cashEmpty"
      :height="260"
    >
      <template #actions>
        <RouterLink :to="{ name: 'owner-reports' }" class="text-sm font-semibold text-primary hover:underline">Laporan</RouterLink>
      </template>
      <CashflowChart v-if="cash" :report="cash" />
    </ChartCard>
    <ChartCard
      title="Terlaris 30 hari"
      subtitle="Berdasarkan jumlah terjual"
      :loading="ownerLoading"
      :error="ownerError"
      :empty="!best?.items.length"
      :height="260"
    >
      <BestSellerChart v-if="best" :report="best" />
    </ChartCard>
  </div>

  <!-- LOGISTIK -->
  <div v-if="auth.user?.role === 'LOGISTIK'" class="mt-6 grid gap-6 xl:grid-cols-3">
    <Card class="gap-4">
      <CardHeader>
        <CardTitle class="text-base">Komposisi stok</CardTitle>
        <CardDescription>{{ formatNumber(stockTotal) }} produk aktif</CardDescription>
      </CardHeader>
      <CardContent class="space-y-5">
        <div v-if="loading" class="h-3 animate-pulse rounded-full bg-muted" />
        <div v-else class="flex h-3 overflow-hidden rounded-full bg-muted" role="img" aria-label="Komposisi status stok">
          <div
            v-for="p in stockParts"
            :key="p.label"
            :class="p.bar"
            :style="{ width: stockTotal ? `${(p.value / stockTotal) * 100}%` : '0%' }"
          />
        </div>
        <ul class="space-y-2.5 text-sm">
          <li v-for="p in stockParts" :key="p.label" class="flex items-center gap-2.5">
            <span class="size-2.5 rounded-full" :class="p.dot" aria-hidden="true" />
            <span class="flex-1 text-muted-foreground">{{ p.label }}</span>
            <span class="num font-semibold">{{ formatNumber(p.value) }}</span>
            <span class="num w-12 text-right text-xs text-muted-foreground">
              {{ stockTotal ? Math.round((p.value / stockTotal) * 100) : 0 }}%
            </span>
          </li>
        </ul>
      </CardContent>
    </Card>

    <ChartCard
      v-if="forecastLoading || forecast?.meta"
      class="xl:col-span-2"
      title="Segera habis (prediksi AI)"
      :subtitle="forecast?.meta ? `Dihitung ${formatDateTime(forecast.meta.generatedAt)}` : undefined"
      :loading="forecastLoading"
      :empty="!urgent.length"
      :height="220"
    >
      <template #actions>
        <RouterLink :to="{ name: 'stock' }" class="text-sm font-semibold text-primary hover:underline">Detail</RouterLink>
      </template>
      <StockoutRiskChart
        v-if="forecast"
        :items="urgent"
        :limit="5"
        :lead-time="Number(forecast.meta?.params.lead_time_days ?? 3)"
        :review-days="Number(forecast.meta?.params.review_days ?? 7)"
        @select="router.push({ name: 'stock' })"
      />
    </ChartCard>
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

    <!-- ADMIN: jumlah per peran → batang proporsional (perbandingan kategori) -->
    <Card v-if="usersByRole.length">
      <CardHeader>
        <CardTitle class="text-base">Pengguna per peran</CardTitle>
        <CardDescription>Akun aktif</CardDescription>
      </CardHeader>
      <CardContent>
        <ul class="space-y-3.5">
          <li v-for="[role, n] in usersByRole" :key="role">
            <div class="mb-1.5 flex items-center justify-between text-sm">
              <span class="font-medium">{{ ROLE_LABEL[role] ?? role }}</span>
              <span class="num font-bold">{{ n }}</span>
            </div>
            <div class="h-2 overflow-hidden rounded-full bg-muted">
              <div class="h-full rounded-full bg-chart-1" :style="{ width: `${(n / maxRole) * 100}%` }" />
            </div>
          </li>
        </ul>
      </CardContent>
    </Card>
  </div>
</template>
