<script setup lang="ts">
/**
 * Tabel standar di atas shadcn Table. Isi sel kustom lewat slot `cell-<key>`:
 *   <DataTable :columns="cols" :rows="rows">
 *     <template #cell-status="{ row }"><ActiveBadge :active="row.isActive" /></template>
 *   </DataTable>
 */
import { InboxIcon } from '@lucide/vue'
import { Empty, EmptyHeader, EmptyMedia, EmptyTitle } from '@/components/ui/empty'
import { Skeleton } from '@/components/ui/skeleton'
import { Table, TableBody, TableCell, TableEmpty, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import type { Column } from './types'

defineProps<{
  columns: Column[]
  rows: any[]
  loading?: boolean
  rowKey?: string
  empty?: string
  clickable?: boolean
}>()
const emit = defineEmits<{ rowClick: [row: any] }>()

const alignClass = (a?: string) => (a === 'right' ? 'text-right' : a === 'center' ? 'text-center' : '')
</script>

<template>
  <Table>
    <TableHeader class="bg-muted/60">
      <TableRow class="hover:bg-transparent">
        <TableHead
          v-for="c in columns"
          :key="c.key"
          :class="['h-11 px-4 text-xs font-semibold tracking-wide text-muted-foreground uppercase', alignClass(c.align), c.class]"
        >
          {{ c.label }}
        </TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      <template v-if="loading && rows.length === 0">
        <TableRow v-for="n in 5" :key="n">
          <TableCell v-for="c in columns" :key="c.key" class="px-4 py-3.5"><Skeleton class="h-4 w-full max-w-40" /></TableCell>
        </TableRow>
      </template>
      <TableEmpty v-else-if="rows.length === 0" :colspan="columns.length">
        <Empty class="p-0 md:p-0">
          <EmptyHeader>
            <EmptyMedia variant="icon"><InboxIcon /></EmptyMedia>
            <EmptyTitle class="text-sm font-medium text-muted-foreground">{{ empty ?? 'Tidak ada data' }}</EmptyTitle>
          </EmptyHeader>
        </Empty>
      </TableEmpty>
      <TableRow
        v-for="(row, i) in rows"
        v-else
        :key="rowKey ? row[rowKey] : i"
        :class="[clickable && 'cursor-pointer', loading && 'opacity-60']"
        :tabindex="clickable ? 0 : undefined"
        @click="clickable && emit('rowClick', row)"
        @keydown.enter="clickable && emit('rowClick', row)"
      >
        <TableCell v-for="c in columns" :key="c.key" :class="['px-4 py-3', alignClass(c.align), c.class]">
          <slot :name="`cell-${c.key}`" :row="row">{{ row[c.key] ?? '—' }}</slot>
        </TableCell>
      </TableRow>
    </TableBody>
  </Table>
</template>
