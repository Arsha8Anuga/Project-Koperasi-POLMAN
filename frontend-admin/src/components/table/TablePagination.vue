<script setup lang="ts">
import PagePagination from '@/components/common/PagePagination.vue'
import type { PageMeta } from '@/types/api'

/** Footer tabel: ringkasan jumlah data + pagination shadcn. Pakai: <TablePagination v-model="page" :meta="meta" /> */
defineProps<{ meta: PageMeta; loading?: boolean }>()
const page = defineModel<number>({ required: true })
</script>

<template>
  <PagePagination v-model:page="page" :total="meta.total" :limit="meta.limit" :disabled="loading">
    <span class="num font-semibold text-foreground">{{ meta.total }}</span> data
    <template v-if="meta.total > 0">
      · menampilkan {{ (meta.page - 1) * meta.limit + 1 }}–{{ Math.min(meta.page * meta.limit, meta.total) }}
    </template>
  </PagePagination>
</template>
