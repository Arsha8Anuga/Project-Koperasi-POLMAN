<script setup lang="ts">
import { SparklesIcon } from '@lucide/vue'
import { ref, watch } from 'vue'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import Modal from '@/components/common/Modal.vue'
import ForecastChart from '@/components/charts/ForecastChart.vue'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { insightApi } from '@/services/api'
import { errorMessage } from '@/services/apiClient'
import type { ForecastDetail, InsightMeta } from '@/types/api'
import { formatDateTime } from '@/utils/format'
import { formatDays, modelLabel, percent, urgency } from '@/utils/insight'

/** Detail prediksi satu produk: chart + angka yang menjelaskan saran restock. */
const props = defineProps<{ productId: string | null }>()
const emit = defineEmits<{ close: [] }>()

const detail = ref<ForecastDetail | null>(null)
const meta = ref<InsightMeta | null>(null)
const loading = ref(false)
const error = ref('')

watch(
  () => props.productId,
  async (id) => {
    detail.value = null
    error.value = ''
    if (!id) return
    loading.value = true
    try {
      const res = await insightApi.forecastDetail(id)
      detail.value = res.product
      meta.value = res.meta
    } catch (e) {
      error.value = errorMessage(e, 'Prediksi belum tersedia')
    } finally {
      loading.value = false
    }
  },
  { immediate: true },
)

const tone = { danger: 'danger', warning: 'warning', ok: 'success' } as const
</script>

<template>
  <Modal
    :open="!!productId"
    :title="detail ? `Prediksi: ${detail.name}` : 'Prediksi penjualan'"
    :description="meta ? `Dihitung AI engine ${formatDateTime(meta.generatedAt)}` : undefined"
    size="lg"
    @close="emit('close')"
  >
    <ErrorAlert v-if="error" :message="error" />
    <div v-else-if="loading || !detail" class="space-y-3">
      <Skeleton class="h-72 rounded-lg" />
      <Skeleton class="h-20 rounded-lg" />
    </div>
    <div v-else class="space-y-4">
      <div class="h-72"><ForecastChart :detail="detail" /></div>

      <dl class="grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
        <div class="rounded-lg bg-muted/60 p-3">
          <dt class="text-xs text-muted-foreground">Stok sekarang</dt>
          <dd class="num text-lg font-bold">{{ detail.stock }} <span class="text-xs font-normal">{{ detail.unit }}</span></dd>
        </div>
        <div class="rounded-lg bg-muted/60 p-3">
          <dt class="text-xs text-muted-foreground">Prediksi terjual</dt>
          <dd class="num text-lg font-bold">±{{ detail.avgDaily }}<span class="text-xs font-normal"> /hari</span></dd>
        </div>
        <div class="rounded-lg bg-muted/60 p-3">
          <dt class="text-xs text-muted-foreground">Stok habis dalam</dt>
          <dd class="mt-0.5">
            <Badge :variant="tone[urgency(detail.daysUntilStockout)]">{{ formatDays(detail.daysUntilStockout) }}</Badge>
          </dd>
        </div>
        <div class="rounded-lg bg-primary p-3 text-primary-foreground">
          <dt class="flex items-center gap-1 text-xs opacity-80"><SparklesIcon class="size-3" /> Saran restock</dt>
          <dd class="num text-lg font-bold">
            {{ detail.suggestedQty > 0 ? `${detail.suggestedQty} ${detail.unit}` : 'Belum perlu' }}
          </dd>
        </div>
      </dl>

      <div class="rounded-lg border p-3 text-xs leading-relaxed text-muted-foreground">
        <p>
          <strong class="text-foreground">Model:</strong> {{ modelLabel(detail.model) }} ·
          <strong class="text-foreground">Galat uji 7 hari (WAPE):</strong> {{ percent(detail.wape) }}
          <template v-if="detail.baselineWape !== null"> vs rata-rata biasa {{ percent(detail.baselineWape) }}</template>
        </p>
        <p>
          Stok pengaman {{ detail.safetyStock }} {{ detail.unit }} · titik pesan ulang
          {{ detail.reorderPoint ?? '—' }} {{ detail.unit }}
          <template v-if="detail.excludedStockoutDays">
            · {{ detail.excludedStockoutDays }} hari stok habis tidak dipakai melatih model
          </template>
        </p>
      </div>
    </div>
  </Modal>
</template>
