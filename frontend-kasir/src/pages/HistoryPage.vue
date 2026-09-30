<script setup lang="ts">
import { CircleAlertIcon, ReceiptIcon } from '@lucide/vue'
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import PagePagination from '@/components/common/PagePagination.vue'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from '@/components/ui/empty'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { Table, TableBody, TableCell, TableEmpty, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import { errorMessage } from '@/services/api'
import { salesApi } from '@/services/salesApi'
import type { PageMeta, Sale } from '@/types'
import { formatDateTime, formatRupiah, todayWib } from '@/utils/format'

const router = useRouter()

const from = ref(todayWib())
const to = ref(todayWib())
const page = ref(1)
const rows = ref<Sale[]>([])
const meta = ref<PageMeta | null>(null)
const loading = ref(false)
const error = ref('')

const pageTotal = computed(() => rows.value.reduce((n, s) => n + s.total, 0))

/** Rentang cepat yang sedang aktif ('0' = hari ini, '6' = 7 hari), '' kalau tanggal diisi manual. */
const quickRange = computed(() => {
  if (to.value !== todayWib()) return ''
  if (from.value === todayWib()) return '0'
  if (from.value === todayWib(-6)) return '6'
  return ''
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await salesApi.mine({ page: page.value, limit: 20, from: from.value, to: to.value })
    rows.value = res.data
    meta.value = res.meta
  } catch (e) {
    error.value = errorMessage(e, 'Gagal memuat riwayat')
  } finally {
    loading.value = false
  }
}

watch([from, to], () => {
  page.value = 1
  load()
})
watch(page, load)
onMounted(load)

function setRange(v: unknown) {
  if (typeof v !== 'string' || v === '') return
  from.value = todayWib(-Number(v))
  to.value = todayWib()
}

function open(s: Sale) {
  router.push({ name: 'invoice', params: { id: s.id } })
}
</script>

<template>
  <div class="h-full overflow-y-auto">
    <div class="mx-auto max-w-5xl px-4 py-6 sm:px-6">
      <div class="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold">Riwayat Transaksi</h1>
          <p class="text-sm text-muted-foreground">Penjualan yang Anda proses. Klik baris untuk membuka struk.</p>
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <ToggleGroup type="single" variant="outline" size="sm" :model-value="quickRange" @update:model-value="setRange">
            <ToggleGroupItem value="0">Hari ini</ToggleGroupItem>
            <ToggleGroupItem value="6">7 hari</ToggleGroupItem>
          </ToggleGroup>
          <Input v-model="from" type="date" class="h-8 w-auto" aria-label="Dari tanggal" :max="to" />
          <span class="text-muted-foreground">–</span>
          <Input v-model="to" type="date" class="h-8 w-auto" aria-label="Sampai tanggal" :min="from" />
        </div>
      </div>

      <Alert v-if="error" variant="destructive" class="mb-4">
        <CircleAlertIcon />
        <AlertDescription>{{ error }}</AlertDescription>
      </Alert>

      <Card class="gap-0 overflow-hidden py-0">
        <Table>
          <TableHeader class="bg-muted/60">
            <TableRow>
              <TableHead class="px-4">Kode</TableHead>
              <TableHead>Waktu</TableHead>
              <TableHead>Pelanggan</TableHead>
              <TableHead>Metode</TableHead>
              <TableHead class="px-4 text-right">Total</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <template v-if="loading && rows.length === 0">
              <TableRow v-for="n in 5" :key="n">
                <TableCell v-for="c in 5" :key="c" class="px-4"><Skeleton class="h-4 w-full" /></TableCell>
              </TableRow>
            </template>
            <TableEmpty v-else-if="rows.length === 0" :colspan="5">
              <Empty class="p-0 md:p-0">
                <EmptyHeader>
                  <EmptyMedia variant="icon"><ReceiptIcon /></EmptyMedia>
                  <EmptyTitle>Belum ada transaksi</EmptyTitle>
                  <EmptyDescription>Tidak ada penjualan pada rentang tanggal ini.</EmptyDescription>
                </EmptyHeader>
              </Empty>
            </TableEmpty>
            <TableRow
              v-for="s in rows"
              :key="s.id"
              class="cursor-pointer"
              tabindex="0"
              @click="open(s)"
              @keydown.enter="open(s)"
            >
              <TableCell class="px-4 font-mono text-[13px] font-semibold">{{ s.code }}</TableCell>
              <TableCell class="text-muted-foreground">{{ formatDateTime(s.createdAt) }}</TableCell>
              <TableCell>{{ s.member?.name ?? s.customerName ?? '—' }}</TableCell>
              <TableCell>
                <Badge :variant="s.payment.method === 'CASH' ? 'outline' : 'soft'">
                  {{ s.payment.method === 'CASH' ? 'Tunai' : 'QRIS' }}
                </Badge>
              </TableCell>
              <TableCell class="px-4 text-right font-semibold">{{ formatRupiah(s.total) }}</TableCell>
            </TableRow>
          </TableBody>
        </Table>

        <PagePagination v-if="meta && meta.total > 0" v-model:page="page" :total="meta.total" :limit="meta.limit" :disabled="loading">
          {{ meta.total }} transaksi · total halaman ini
          <strong class="num text-foreground">{{ formatRupiah(pageTotal) }}</strong>
        </PagePagination>
      </Card>
    </div>
  </div>
</template>
