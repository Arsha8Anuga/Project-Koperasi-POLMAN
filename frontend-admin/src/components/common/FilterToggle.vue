<script setup lang="ts" generic="T extends string | boolean">
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'

/**
 * Filter pilihan tunggal (shadcn ToggleGroup). Nilai boleh '' (= semua) atau boolean;
 * diubah ke string internal karena ToggleGroup hanya menerima string.
 */
const props = defineProps<{ options: { value: T | ''; label: string }[]; label?: string }>()
const model = defineModel<T | ''>({ required: true })

const key = (v: T | '') => (v === '' ? '__all' : String(v))

function onUpdate(v: unknown) {
  const opt = props.options.find((o) => key(o.value) === v)
  if (opt) model.value = opt.value // klik ulang item aktif (v = undefined) diabaikan
}
</script>

<template>
  <ToggleGroup type="single" variant="outline" :model-value="key(model)" :aria-label="label" @update:model-value="onUpdate">
    <ToggleGroupItem v-for="o in options" :key="key(o.value)" :value="key(o.value)" class="px-3">{{ o.label }}</ToggleGroupItem>
  </ToggleGroup>
</template>
