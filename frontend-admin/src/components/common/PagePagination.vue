<script setup lang="ts">
import { ChevronLeftIcon, ChevronRightIcon } from '@lucide/vue'
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination'

/**
 * Pagination shadcn untuk `meta` dari API (dokumen 04) — ISI FILE INI IDENTIK di kedua app.
 * Pakai: <PagePagination v-model:page="page" :total="meta.total" :limit="meta.limit" />
 */
defineProps<{ total: number; limit: number; disabled?: boolean }>()
const page = defineModel<number>('page', { required: true })
</script>

<template>
  <div class="flex flex-wrap items-center justify-between gap-3 border-t px-4 py-3 text-sm">
    <span class="text-muted-foreground"><slot /></span>
    <Pagination
      v-if="total > limit"
      v-slot="{ page: current }"
      v-model:page="page"
      :total="total"
      :items-per-page="limit"
      :sibling-count="1"
      :disabled="disabled"
      show-edges
      class="mx-0 w-auto"
    >
      <PaginationContent v-slot="{ items }">
        <PaginationPrevious size="sm" class="px-2.5" aria-label="Halaman sebelumnya"><ChevronLeftIcon /><span class="hidden sm:inline">Sebelumnya</span></PaginationPrevious>
        <template v-for="(item, index) in items" :key="index">
          <PaginationItem
            v-if="item.type === 'page'"
            :value="item.value"
            :is-active="item.value === current"
            size="icon-sm"
            class="num"
          >
            {{ item.value }}
          </PaginationItem>
          <PaginationEllipsis v-else :index="index" />
        </template>
        <PaginationNext size="sm" class="px-2.5" aria-label="Halaman berikutnya"><span class="hidden sm:inline">Berikutnya</span><ChevronRightIcon /></PaginationNext>
      </PaginationContent>
    </Pagination>
  </div>
</template>
