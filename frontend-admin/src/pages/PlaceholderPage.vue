<script setup lang="ts">
import DataTable, { type Column } from '@/components/table/DataTable.vue'

interface Row { name: string; stock: number }
const columns: Column<Row>[] = [
  { key: 'name', label: 'Nama' },
  { key: 'stock', label: 'Stok' },
]
const rows: Row[] = [{ name: 'Buku Tulis', stock: 48 }, { name: 'Pulpen', stock: 3 }]
</script>

<template>
  <div class="p-8">
    <DataTable :columns="columns" :rows="rows" />
  </div>
</template>