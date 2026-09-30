<script setup lang="ts">
import { PlusIcon, SquarePenIcon } from '@lucide/vue'
import { reactive, ref } from 'vue'
import ActiveBadge from '@/components/common/ActiveBadge.vue'
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
import { Label } from '@/components/ui/label'
import { Spinner } from '@/components/ui/spinner'
import { Switch } from '@/components/ui/switch'
import { usePagination } from '@/composables/usePagination'
import { memberApi } from '@/services/api'
import { ApiException, errorMessage } from '@/services/apiClient'
import { useToast } from '@/composables/useToast'
import type { Member } from '@/types/api'
import { formatDate, todayWib } from '@/utils/format'

const toast = useToast()
const list = usePagination<Member, { search: string; isActive: boolean | '' }>((q) => memberApi.list(q), {
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
  { key: 'memberNumber', label: 'No. anggota' },
  { key: 'name', label: 'Nama' },
  { key: 'phone', label: 'Telepon' },
  { key: 'joinedAt', label: 'Bergabung' },
  { key: 'isActive', label: 'Status' },
  { key: 'actions', label: '', align: 'right' },
]

const open = ref(false)
const editing = ref<Member | null>(null)
const form = reactive({ name: '', phone: '', joinedAt: todayWib(), isActive: true })
const errors = reactive<Record<string, string>>({})
const saving = ref(false)

function openForm(m: Member | null) {
  editing.value = m
  Object.assign(form, {
    name: m?.name ?? '',
    phone: m?.phone ?? '',
    joinedAt: m?.joinedAt ?? todayWib(),
    isActive: m?.isActive ?? true,
  })
  for (const k of Object.keys(errors)) delete errors[k]
  open.value = true
}

async function save() {
  for (const k of Object.keys(errors)) delete errors[k]
  if (!form.name.trim()) errors.name = 'Nama wajib diisi'
  if (form.phone.trim() && !/^\+?[0-9]{8,15}$/.test(form.phone.trim())) errors.phone = '8–15 digit angka'
  if (Object.keys(errors).length) return
  saving.value = true
  const phone = form.phone.trim() || null
  try {
    if (editing.value) {
      await memberApi.update(editing.value.id, { name: form.name.trim(), phone, isActive: form.isActive })
      toast.success('Data anggota diperbarui')
    } else {
      const m = await memberApi.create({ name: form.name.trim(), phone, joinedAt: form.joinedAt })
      toast.success(`Anggota didaftarkan dengan nomor ${m.memberNumber}`)
    }
    open.value = false
    list.reload()
  } catch (e) {
    if (e instanceof ApiException) Object.assign(errors, e.fieldErrors())
    if (!Object.keys(errors).length) errors.name = errorMessage(e)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <PageHeader title="Anggota Koperasi" subtitle="Nomor anggota dipakai kasir untuk mencatat pembelian anggota.">
    <Button @click="openForm(null)"><PlusIcon /> Daftarkan anggota</Button>
  </PageHeader>

  <Card class="gap-0 overflow-hidden py-0">
    <div class="flex flex-wrap items-center gap-2 border-b p-4">
      <SearchInput v-model="list.filters.search" placeholder="Cari nomor, nama, atau telepon" />
      <FilterToggle v-model="list.filters.isActive" :options="activeOptions" label="Status" />
    </div>
    <ErrorAlert v-if="list.error.value" :message="list.error.value" class="m-4 w-auto" />
    <DataTable :columns="columns" :rows="list.rows.value"
      :start-index="(list.meta.value.page - 1) * list.meta.value.limit" :loading="list.loading.value" row-key="id" empty="Belum ada anggota">
      <template #cell-memberNumber="{ row }"><span class="font-mono text-[13px] font-semibold">{{ row.memberNumber }}</span></template>
      <template #cell-name="{ row }"><span class="font-semibold">{{ row.name }}</span></template>
      <template #cell-phone="{ row }"><span class="text-muted-foreground">{{ row.phone ?? '—' }}</span></template>
      <template #cell-joinedAt="{ row }"><span class="text-muted-foreground">{{ formatDate(row.joinedAt) }}</span></template>
      <template #cell-isActive="{ row }"><ActiveBadge :active="row.isActive" /></template>
      <template #cell-actions="{ row }">
        <Button variant="ghost" size="sm" @click="openForm(row)"><SquarePenIcon /> Ubah</Button>
      </template>
    </DataTable>
    <TablePagination v-model="list.page.value" :meta="list.meta.value" :loading="list.loading.value" />
  </Card>

  <Modal :open="open" :title="editing ? `Ubah anggota ${editing.memberNumber}` : 'Daftarkan anggota'" @close="open = false">
    <form class="space-y-4" @submit.prevent="save">
      <p v-if="!editing" class="rounded-md bg-muted/60 px-3 py-2 text-sm text-muted-foreground">
        Nomor anggota (KOP-NNN) dibuat otomatis setelah disimpan.
      </p>
      <FormField label="Nama" for="m-name" required :error="errors.name">
        <Input id="m-name" v-model="form.name" :aria-invalid="!!errors.name || undefined" maxlength="60" />
      </FormField>
      <FormField v-if="!editing" label="Tanggal bergabung" for="m-join" :error="errors.joinedAt">
        <Input id="m-join" v-model="form.joinedAt" type="date" />
      </FormField>
      <FormField label="Telepon" for="m-phone" :error="errors.phone" hint="Opsional">
        <Input id="m-phone" v-model="form.phone" inputmode="tel" placeholder="0812…" :aria-invalid="!!errors.phone || undefined" />
      </FormField>
      <div v-if="editing" class="flex items-center gap-3">
        <Switch id="m-active" v-model="form.isActive" />
        <Label for="m-active">
          Aktif <span class="font-normal text-muted-foreground">(anggota nonaktif tidak bisa dipakai di kasir)</span>
        </Label>
      </div>
      <DialogFooter class="pt-2">
        <Button type="button" variant="outline" @click="open = false">Batal</Button>
        <Button type="submit" :disabled="saving"><Spinner v-if="saving" /> Simpan</Button>
      </DialogFooter>
    </form>
  </Modal>
</template>
