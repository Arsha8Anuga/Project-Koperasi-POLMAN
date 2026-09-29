<script setup lang="ts" generic="T extends object">
export interface Column<T> {
  key: keyof T & string
  label: string
  sortable?: boolean
  render?: (row: T) => string
}

const props = defineProps<{
  columns: Column<T>[]
  rows: T[]
  loading?: boolean
  meta?: { page: number; limit: number; total: number; totalPages: number }
}>()
const emit = defineEmits<{ 'update:page': [number]; sort: [string] }>()

function cell(row: T, col: Column<T>) {
  if (col.render) return col.render(row)
  const value = (row as Record<string, unknown>)[col.key]
  return String(value ?? '-')
}
</script>

<template>
  <div class="overflow-hidden rounded-xl border bg-white">
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="border-b bg-gray-50 text-left text-gray-500">
          <tr>
            <th
              v-for="col in columns"
              :key="col.key"
              class="px-4 py-3 font-medium"
              :class="col.sortable && 'cursor-pointer select-none hover:text-gray-700'"
              @click="col.sortable && emit('sort', col.key)"
            >
              {{ col.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td :colspan="columns.length" class="px-4 py-8 text-center text-gray-400">Memuat data...</td>
          </tr>
          <tr v-else-if="rows.length === 0">
            <td :colspan="columns.length" class="px-4 py-8 text-center text-gray-400">Tidak ada data</td>
          </tr>
          <tr v-for="(row, i) in rows" v-else :key="i" class="border-b last:border-0 hover:bg-gray-50">
            <td v-for="col in columns" :key="col.key" class="px-4 py-3">
              <slot :name="`cell-${col.key}`" :row="row">{{ cell(row, col) }}</slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="meta" class="flex items-center justify-between border-t px-4 py-3 text-sm text-gray-500">
      <span>Halaman {{ meta.page }} dari {{ meta.totalPages || 1 }} · {{ meta.total }} data</span>
      <div class="flex gap-2">
        <button
          class="rounded-lg border px-3 py-1 disabled:opacity-40"
          :disabled="meta.page <= 1"
          @click="emit('update:page', meta.page - 1)"
        >
          Sebelumnya
        </button>
        <button
          class="rounded-lg border px-3 py-1 disabled:opacity-40"
          :disabled="meta.page >= meta.totalPages"
          @click="emit('update:page', meta.page + 1)"
        >
          Berikutnya
        </button>
      </div>
    </div>
  </div>
</template>