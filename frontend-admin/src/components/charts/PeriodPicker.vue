<script setup lang="ts">
import { onMounted, reactive } from 'vue'
import { Input } from '@/components/ui/input'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import type { Granularity, ReportPeriod } from '@/types/api'
import { todayWib } from '@/utils/format'

const emit = defineEmits<{ change: [ReportPeriod] }>()

const options: { value: Granularity; label: string; days: number }[] = [
  { value: 'day', label: 'Harian', days: 29 },
  { value: 'week', label: 'Mingguan', days: 7 * 12 - 1 },
  { value: 'month', label: 'Bulanan', days: 365 },
  { value: 'year', label: 'Tahunan', days: 365 * 5 },
]

const state = reactive<ReportPeriod>({ granularity: 'day', from: todayWib(-29), to: todayWib() })

/** ToggleGroup mengirim undefined saat item aktif diklik ulang → abaikan. */
function pick(v: unknown) {
  const opt = options.find((o) => o.value === v)
  if (!opt) return
  state.granularity = opt.value
  state.from = todayWib(-opt.days)
  state.to = todayWib()
  emit('change', { ...state })
}

function onDate() {
  if (state.from && state.to && state.from <= state.to) emit('change', { ...state })
}

onMounted(() => emit('change', { ...state }))
</script>

<template>
  <div class="flex flex-wrap items-center gap-2">
    <ToggleGroup
      type="single"
      variant="outline"
      size="sm"
      :model-value="state.granularity"
      aria-label="Periode"
      @update:model-value="pick"
    >
      <ToggleGroupItem v-for="o in options" :key="o.value" :value="o.value">{{ o.label }}</ToggleGroupItem>
    </ToggleGroup>
    <Input v-model="state.from" type="date" class="h-8 w-auto" aria-label="Dari tanggal" :max="state.to" @change="onDate" />
    <span class="text-muted-foreground">–</span>
    <Input v-model="state.to" type="date" class="h-8 w-auto" aria-label="Sampai tanggal" :min="state.from" @change="onDate" />
  </div>
</template>
