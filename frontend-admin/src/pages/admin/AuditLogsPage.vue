<script setup lang="ts">
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import DataTable from '@/components/table/DataTable.vue'
import TablePagination from '@/components/table/TablePagination.vue'
import type { Column } from '@/components/table/types'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { NativeSelect, NativeSelectOption } from '@/components/ui/native-select'
import { usePagination } from '@/composables/usePagination'
import { auditApi } from '@/services/api'
import type { AuditAction, AuditLog, AuditModule } from '@/types/api'
import { formatDateTime, todayWib } from '@/utils/format'

const modules: Record<AuditModule, string> = {
  AUTH: 'Autentikasi',
  USER: 'Pengguna',
  MEMBER: 'Anggota',
  CATEGORY: 'Kategori',
  PRODUCT: 'Produk',
  SUPPLIER: 'Supplier',
  RESTOCK: 'Restock',
  SALE: 'Penjualan',
  AI: 'AI Engine',
}
const actions: Record<AuditAction, string> = {
  LOGIN: 'Masuk',
  LOGOUT: 'Keluar',
  CREATE: 'Buat',
  UPDATE: 'Ubah',
  DEACTIVATE: 'Nonaktifkan',
  ACTIVATE: 'Aktifkan',
  RESET_PASSWORD: 'Reset password',
  SALE: 'Penjualan',
  RESTOCK: 'Restock',
  RECOMPUTE: 'Hitung ulang AI',
}
const actionTone = (a: AuditAction) =>
  a === 'DEACTIVATE' || a === 'RESET_PASSWORD'
    ? 'danger'
    : a === 'CREATE' || a === 'ACTIVATE'
      ? 'success'
      : a === 'LOGIN' || a === 'LOGOUT'
        ? 'outline'
        : 'soft'

const list = usePagination<AuditLog, { module: AuditModule | ''; action: AuditAction | ''; from: string; to: string }>(
  (q) => auditApi.list(q),
  { module: '', action: '', from: todayWib(-6), to: todayWib() },
  25,
)
list.load()

const columns: Column[] = [
  { key: 'createdAt', label: 'Waktu', class: 'whitespace-nowrap' },
  { key: 'user', label: 'Pengguna' },
  { key: 'action', label: 'Aksi' },
  { key: 'description', label: 'Keterangan' },
  { key: 'ip', label: 'IP' },
]
</script>

<template>
  <PageHeader title="Audit Trail" subtitle="Catatan semua aksi penting: login, perubahan data, penjualan, dan restock." />

  <Card class="gap-0 overflow-hidden py-0">
    <div class="flex flex-wrap items-center gap-2 border-b p-4">
      <NativeSelect v-model="list.filters.module" aria-label="Modul">
        <NativeSelectOption value="">Semua modul</NativeSelectOption>
        <NativeSelectOption v-for="(label, key) in modules" :key="key" :value="key">{{ label }}</NativeSelectOption>
      </NativeSelect>
      <NativeSelect v-model="list.filters.action" aria-label="Aksi">
        <NativeSelectOption value="">Semua aksi</NativeSelectOption>
        <NativeSelectOption v-for="(label, key) in actions" :key="key" :value="key">{{ label }}</NativeSelectOption>
      </NativeSelect>
      <Input v-model="list.filters.from" type="date" class="w-auto" aria-label="Dari" :max="list.filters.to" />
      <span class="text-muted-foreground">–</span>
      <Input v-model="list.filters.to" type="date" class="w-auto" aria-label="Sampai" :min="list.filters.from" />
    </div>
    <ErrorAlert v-if="list.error.value" :message="list.error.value" class="m-4 w-auto" />
    <DataTable
      :columns="columns"
      :rows="list.rows.value"
      :loading="list.loading.value"
      row-key="id"
      empty="Tidak ada aktivitas pada filter ini"
    >
      <template #cell-createdAt="{ row }"><span class="text-muted-foreground">{{ formatDateTime(row.createdAt) }}</span></template>
      <template #cell-user="{ row }">
        <p class="font-semibold">{{ row.user.name }}</p>
        <p class="text-xs text-muted-foreground">{{ row.user.role }}</p>
      </template>
      <template #cell-action="{ row }">
        <Badge :variant="actionTone(row.action)">{{ actions[row.action as AuditAction] ?? row.action }}</Badge>
        <p class="mt-1 text-xs text-muted-foreground">{{ modules[row.module as AuditModule] ?? row.module }}</p>
      </template>
      <template #cell-description="{ row }"><span class="whitespace-normal">{{ row.description }}</span></template>
      <template #cell-ip="{ row }"><span class="font-mono text-xs text-muted-foreground">{{ row.ip ?? '—' }}</span></template>
    </DataTable>
    <TablePagination v-model="list.page.value" :meta="list.meta.value" :loading="list.loading.value" />
  </Card>
</template>
