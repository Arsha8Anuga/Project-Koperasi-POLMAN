<script setup lang="ts">
import { ActivityIcon, CircleCheckIcon, CpuIcon, RefreshCwIcon, ServerOffIcon, SparklesIcon } from '@lucide/vue'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import StatCard from '@/components/common/StatCard.vue'
import DataTable from '@/components/table/DataTable.vue'
import type { Column } from '@/components/table/types'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Spinner } from '@/components/ui/spinner'
import { useToast } from '@/composables/useToast'
import { insightApi } from '@/services/api'
import { ApiException, errorMessage } from '@/services/apiClient'
import type { AiJob, AiStatus, InsightKind, JobStatus, JobTrigger } from '@/types/api'
import { formatDateTime, formatNumber } from '@/utils/format'

/**
 * Halaman ADMIN: memantau AI engine (container terpisah) dan meminta perhitungan ulang.
 * Engine sendiri yang mengerjakan job; backend hanya menaruh job PENDING di antrean.
 */
const toast = useToast()
const status = ref<AiStatus | null>(null)
const loading = ref(true)
const error = ref('')
const submitting = ref(false)
let timer: ReturnType<typeof setTimeout> | undefined

const KIND_LABEL: Record<InsightKind, string> = {
  association_rules: 'Produk sering dibeli bersamaan',
  forecast: 'Prediksi penjualan & restock',
}
const STATUS_LABEL: Record<JobStatus, string> = {
  PENDING: 'Menunggu',
  RUNNING: 'Berjalan',
  DONE: 'Selesai',
  FAILED: 'Gagal',
}
const TRIGGER_LABEL: Record<JobTrigger, string> = { MANUAL: 'Manual', SCHEDULE: 'Terjadwal', SEED: 'Seed data' }
const statusTone = (s: JobStatus) =>
  s === 'DONE' ? 'success' : s === 'FAILED' ? 'danger' : s === 'RUNNING' ? 'warning' : 'soft'

async function load(silent = false) {
  if (!silent) loading.value = true
  try {
    status.value = await insightApi.status()
    error.value = ''
  } catch (e) {
    error.value = errorMessage(e, 'Gagal memuat status AI engine')
  } finally {
    loading.value = false
    schedule()
  }
}

/** Selama ada job aktif, status dicek tiap 5 detik; kalau tidak, tiap 60 detik (denyut engine). */
function schedule() {
  clearTimeout(timer)
  timer = setTimeout(() => load(true), status.value?.activeJob ? 5000 : 60000)
}

async function recompute() {
  submitting.value = true
  try {
    await insightApi.recompute()
    toast.success('Perhitungan ulang dimasukkan ke antrean')
  } catch (e) {
    if (e instanceof ApiException && e.code === 'JOB_IN_PROGRESS') toast.info('Masih ada perhitungan yang berjalan')
    else toast.error(errorMessage(e, 'Gagal meminta perhitungan ulang'))
  } finally {
    submitting.value = false
    await load(true)
  }
}

onMounted(() => load())
onBeforeUnmount(() => clearTimeout(timer))

const engine = computed(() => status.value?.engine)
const active = computed(() => status.value?.activeJob ?? null)

const stat = (s: Record<string, unknown> | null | undefined, key: string) => {
  const v = s?.[key]
  return typeof v === 'number' ? formatNumber(v) : '—'
}

function duration(job: AiJob): string {
  if (!job.startedAt || !job.finishedAt) return '—'
  const sec = (new Date(job.finishedAt).getTime() - new Date(job.startedAt).getTime()) / 1000
  return sec < 60 ? `${sec.toFixed(1)} dtk` : `${Math.round(sec / 60)} mnt`
}

const columns: Column[] = [
  { key: 'requestedAt', label: 'Diminta', class: 'whitespace-nowrap' },
  { key: 'trigger', label: 'Pemicu' },
  { key: 'status', label: 'Status' },
  { key: 'duration', label: 'Durasi', class: 'text-right' },
  { key: 'note', label: 'Keterangan' },
]
</script>

<template>
  <PageHeader
    title="AI Engine"
    subtitle="Mesin analisis terpisah (bukan chatbot): association rules untuk rekomendasi produk dan forecasting untuk saran restock."
  >
    <Button :disabled="submitting || !!active || loading" @click="recompute">
      <Spinner v-if="submitting || active" />
      <RefreshCwIcon v-else />
      {{ active ? 'Sedang menghitung…' : 'Hitung ulang' }}
    </Button>
  </PageHeader>

  <ErrorAlert v-if="error" :message="error" class="mb-6" />

  <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
    <StatCard
      label="Status engine"
      :value="loading ? '…' : engine?.online ? 'Online' : 'Offline'"
      :icon="engine?.online ? CpuIcon : ServerOffIcon"
      :tone="engine?.online ? 'success' : 'danger'"
      :hint="engine?.lastSeenAt ? `terakhir terlihat ${formatDateTime(engine.lastSeenAt)}` : 'belum pernah terhubung'"
    />
    <StatCard
      label="Versi"
      :value="engine?.version ?? '—'"
      :icon="SparklesIcon"
      tone="neutral"
      :hint="engine?.intervalMinutes ? `hitung otomatis tiap ${engine.intervalMinutes} menit` : undefined"
    />
    <StatCard
      label="Job aktif"
      :value="active ? STATUS_LABEL[active.status] : 'Tidak ada'"
      :icon="active ? ActivityIcon : CircleCheckIcon"
      :tone="active ? 'warning' : 'primary'"
      :hint="active ? `diminta ${formatDateTime(active.requestedAt)}` : undefined"
    />
  </div>

  <p v-if="!loading && engine && !engine.online" class="mt-3 text-sm text-muted-foreground">
    Engine tidak mengirim denyut lebih dari 3 menit. Job yang diminta tetap tersimpan dan dikerjakan begitu container
    <code class="font-mono">ai-engine</code> berjalan lagi.
  </p>

  <div class="mt-6 grid gap-6 lg:grid-cols-2">
    <Card v-for="i in status?.insights ?? []" :key="i.kind">
      <CardHeader>
        <CardTitle class="text-base">{{ KIND_LABEL[i.kind] ?? i.kind }}</CardTitle>
        <CardDescription>
          {{ i.generatedAt ? `Dihitung ${formatDateTime(i.generatedAt)}` : 'Belum pernah dihitung' }}
        </CardDescription>
        <CardAction>
          <Badge :variant="i.generatedAt ? 'success' : 'soft'">{{ i.generatedAt ? 'Tersedia' : 'Kosong' }}</Badge>
        </CardAction>
      </CardHeader>
      <CardContent v-if="i.stats">
        <dl v-if="i.kind === 'association_rules'" class="grid grid-cols-3 gap-3 text-sm">
          <div><dt class="text-muted-foreground">Transaksi</dt><dd class="num font-bold">{{ stat(i.stats, 'transactions') }}</dd></div>
          <div><dt class="text-muted-foreground">Itemset sering</dt><dd class="num font-bold">{{ stat(i.stats, 'frequentItemsets') }}</dd></div>
          <div><dt class="text-muted-foreground">Aturan</dt><dd class="num font-bold">{{ stat(i.stats, 'rules') }}</dd></div>
        </dl>
        <dl v-else class="grid grid-cols-3 gap-3 text-sm">
          <div><dt class="text-muted-foreground">Produk</dt><dd class="num font-bold">{{ stat(i.stats, 'products') }}</dd></div>
          <div><dt class="text-muted-foreground">Perlu restock</dt><dd class="num font-bold">{{ stat(i.stats, 'reorderNeeded') }}</dd></div>
          <div>
            <dt class="text-muted-foreground">Rata-rata WAPE</dt>
            <dd class="num font-bold">
              {{ typeof i.stats.avgWape === 'number' ? `${Math.round(i.stats.avgWape * 100)}%` : '—' }}
            </dd>
          </div>
        </dl>
      </CardContent>
    </Card>
  </div>

  <Card class="mt-6 gap-0 overflow-hidden py-0">
    <CardHeader class="border-b py-4">
      <CardTitle class="text-base">Riwayat perhitungan</CardTitle>
    </CardHeader>
    <DataTable
      :columns="columns"
      :rows="status?.recentJobs ?? []"
      :loading="loading"
      row-key="id"
      empty="Belum ada perhitungan"
    >
      <template #cell-requestedAt="{ row }">
        <span class="text-muted-foreground">{{ formatDateTime(row.requestedAt) }}</span>
      </template>
      <template #cell-trigger="{ row }">
        <p>{{ TRIGGER_LABEL[row.trigger as JobTrigger] ?? row.trigger }}</p>
        <p v-if="row.requestedBy" class="text-xs text-muted-foreground">{{ row.requestedBy.name }}</p>
      </template>
      <template #cell-status="{ row }">
        <Badge :variant="statusTone(row.status)">{{ STATUS_LABEL[row.status as JobStatus] ?? row.status }}</Badge>
      </template>
      <template #cell-duration="{ row }"><span class="num">{{ duration(row as AiJob) }}</span></template>
      <template #cell-note="{ row }">
        <span v-if="row.error" class="whitespace-normal text-destructive">{{ row.error }}</span>
        <span v-else class="text-muted-foreground">{{ (row.kinds as InsightKind[]).map((k) => KIND_LABEL[k] ?? k).join(', ') }}</span>
      </template>
    </DataTable>
  </Card>
</template>
