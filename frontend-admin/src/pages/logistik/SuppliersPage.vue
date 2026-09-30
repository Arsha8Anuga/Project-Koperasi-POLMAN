<script setup lang="ts">
import { PlusIcon, SquarePenIcon } from '@lucide/vue'
import { reactive, ref } from 'vue'
import ActiveBadge from '@/components/common/ActiveBadge.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import FilterToggle from '@/components/common/FilterToggle.vue'
import Modal from '@/components/common/Modal.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import SearchInput from '@/components/common/SearchInput.vue'
import FormField from '@/components/form/FormField.vue'
import DataTable from '@/components/table/DataTable.vue'
import TablePagination from '@/components/table/TablePagination.vue'
import type { Column } from '@/components/table/types'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { DialogFooter } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Spinner } from '@/components/ui/spinner'
import { Textarea } from '@/components/ui/textarea'
import { usePagination } from '@/composables/usePagination'
import { supplierApi } from '@/services/api'
import { ApiException, errorMessage } from '@/services/apiClient'
import { useToast } from '@/composables/useToast'
import type { Supplier, SupplierInput } from '@/types/api'

const toast = useToast()
const list = usePagination<Supplier, { search: string; isActive: boolean | '' }>((q) => supplierApi.list(q), {
  search: '',
  isActive: '',
})
list.load()

const activeOptions: { value: boolean | ''; label: string }[] = [
  { value: '', label: 'Semua' },
  { value: true, label: 'Aktif' },
  { value: false, label: 'Nonaktif' },
]

const columns: Column[] = [
  { key: 'supplier', label: 'Supplier' },
  { key: 'contact', label: 'Kontak' },
  { key: 'address', label: 'Alamat' },
  { key: 'isActive', label: 'Status' },
  { key: 'actions', label: '', align: 'right' },
]

const empty: SupplierInput = { supplierCode: '', name: '', contactPerson: '', phone: '', email: '', address: '', notes: '' }
const open = ref(false)
const editing = ref<Supplier | null>(null)
const form = reactive<Record<keyof SupplierInput, string>>({ ...empty } as Record<keyof SupplierInput, string>)
const errors = reactive<Record<string, string>>({})
const saving = ref(false)

function openForm(s: Supplier | null) {
  editing.value = s
  for (const k of Object.keys(empty) as (keyof SupplierInput)[]) form[k] = s?.[k] ?? ''
  for (const k of Object.keys(errors)) delete errors[k]
  open.value = true
}

async function save() {
  for (const k of Object.keys(errors)) delete errors[k]
  if (!form.supplierCode.trim()) errors.supplierCode = 'Kode wajib diisi'
  if (!form.name.trim()) errors.name = 'Nama wajib diisi'
  if (Object.keys(errors).length) return
  saving.value = true
  const body = Object.fromEntries(
    Object.entries(form).map(([k, v]) => [k, v.trim() || null]),
  ) as unknown as SupplierInput
  try {
    if (editing.value) await supplierApi.update(editing.value.id, body)
    else await supplierApi.create(body)
    toast.success(editing.value ? 'Supplier diperbarui' : 'Supplier dibuat')
    open.value = false
    list.reload()
  } catch (e) {
    if (e instanceof ApiException) Object.assign(errors, e.fieldErrors())
    if (!Object.keys(errors).length) errors.name = errorMessage(e)
  } finally {
    saving.value = false
  }
}

const target = ref<Supplier | null>(null)
const toggling = ref(false)
async function toggle() {
  if (!target.value) return
  toggling.value = true
  try {
    const s = await supplierApi.setStatus(target.value.id, !target.value.isActive)
    toast.success(`${s.name} ${s.isActive ? 'diaktifkan' : 'dinonaktifkan'}`)
    target.value = null
    list.reload()
  } catch (e) {
    toast.error(errorMessage(e))
  } finally {
    toggling.value = false
  }
}
</script>

<template>
  <PageHeader title="Supplier" subtitle="Supplier nonaktif tidak bisa dipilih saat restock.">
    <Button @click="openForm(null)"><PlusIcon /> Supplier baru</Button>
  </PageHeader>

  <Card class="gap-0 overflow-hidden py-0">
    <div class="flex flex-wrap items-center gap-2 border-b p-4">
      <SearchInput v-model="list.filters.search" placeholder="Cari kode, nama, atau kontak" />
      <FilterToggle v-model="list.filters.isActive" :options="activeOptions" label="Status" />
    </div>
    <ErrorAlert v-if="list.error.value" :message="list.error.value" class="m-4 w-auto" />
    <DataTable :columns="columns" :rows="list.rows.value"
      :start-index="(list.meta.value.page - 1) * list.meta.value.limit" :loading="list.loading.value" row-key="id" empty="Belum ada supplier">
      <template #cell-supplier="{ row }">
        <p class="font-semibold">{{ row.name }}</p>
        <p class="font-mono text-xs text-muted-foreground">{{ row.supplierCode }}</p>
      </template>
      <template #cell-contact="{ row }">
        <p>{{ row.contactPerson ?? '—' }}</p>
        <p class="text-xs text-muted-foreground">{{ [row.phone, row.email].filter(Boolean).join(' · ') }}</p>
      </template>
      <template #cell-address="{ row }">
        <span class="line-clamp-2 max-w-xs whitespace-normal text-muted-foreground">{{ row.address ?? '—' }}</span>
      </template>
      <template #cell-isActive="{ row }"><ActiveBadge :active="row.isActive" /></template>
      <template #cell-actions="{ row }">
        <div class="flex justify-end gap-1">
          <Button variant="ghost" size="sm" @click="openForm(row)"><SquarePenIcon /> Ubah</Button>
          <Button variant="ghost" size="sm" :class="row.isActive && 'text-destructive hover:text-destructive'" @click="target = row">
            {{ row.isActive ? 'Nonaktifkan' : 'Aktifkan' }}
          </Button>
        </div>
      </template>
    </DataTable>
    <TablePagination v-model="list.page.value" :meta="list.meta.value" :loading="list.loading.value" />
  </Card>

  <Modal :open="open" :title="editing ? 'Ubah supplier' : 'Supplier baru'" size="lg" @close="open = false">
    <form class="space-y-4" @submit.prevent="save">
      <div class="grid gap-4 sm:grid-cols-[10rem_1fr]">
        <FormField label="Kode" for="s-code" required :error="errors.supplierCode">
          <Input
            id="s-code"
            v-model="form.supplierCode"
            class="font-mono uppercase"
            :aria-invalid="!!errors.supplierCode || undefined"
            maxlength="20"
            placeholder="SUP-001"
          />
        </FormField>
        <FormField label="Nama" for="s-name" required :error="errors.name">
          <Input id="s-name" v-model="form.name" :aria-invalid="!!errors.name || undefined" maxlength="120" />
        </FormField>
      </div>
      <div class="grid gap-4 sm:grid-cols-3">
        <FormField label="Kontak" for="s-cp" :error="errors.contactPerson">
          <Input id="s-cp" v-model="form.contactPerson" maxlength="60" />
        </FormField>
        <FormField label="Telepon" for="s-phone" :error="errors.phone">
          <Input id="s-phone" v-model="form.phone" inputmode="tel" placeholder="0812…" :aria-invalid="!!errors.phone || undefined" />
        </FormField>
        <FormField label="Email" for="s-email" :error="errors.email">
          <Input id="s-email" v-model="form.email" type="email" :aria-invalid="!!errors.email || undefined" />
        </FormField>
      </div>
      <FormField label="Alamat" for="s-address" :error="errors.address">
        <Input id="s-address" v-model="form.address" maxlength="300" />
      </FormField>
      <FormField label="Catatan" for="s-notes" :error="errors.notes">
        <Textarea id="s-notes" v-model="form.notes" class="min-h-20" maxlength="300" />
      </FormField>
      <DialogFooter class="pt-2">
        <Button type="button" variant="outline" @click="open = false">Batal</Button>
        <Button type="submit" :disabled="saving"><Spinner v-if="saving" /> Simpan</Button>
      </DialogFooter>
    </form>
  </Modal>

  <ConfirmModal
    :open="!!target"
    :title="target?.isActive ? 'Nonaktifkan supplier?' : 'Aktifkan supplier?'"
    :message="target?.isActive ? `${target?.name} tidak bisa dipilih lagi saat restock.` : `${target?.name} bisa dipilih lagi saat restock.`"
    :confirm-text="target?.isActive ? 'Nonaktifkan' : 'Aktifkan'"
    :danger="target?.isActive"
    :loading="toggling"
    @confirm="toggle"
    @cancel="target = null"
  />
</template>
