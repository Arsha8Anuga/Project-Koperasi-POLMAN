<script setup lang="ts">
import { PlusIcon, SquarePenIcon } from '@lucide/vue'
import { onMounted, reactive, ref } from 'vue'
import ActiveBadge from '@/components/common/ActiveBadge.vue'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import Modal from '@/components/common/Modal.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import FormField from '@/components/form/FormField.vue'
import DataTable from '@/components/table/DataTable.vue'
import type { Column } from '@/components/table/types'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { DialogFooter } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Spinner } from '@/components/ui/spinner'
import { Switch } from '@/components/ui/switch'
import { categoryApi } from '@/services/api'
import { ApiException, errorMessage } from '@/services/apiClient'
import { useToast } from '@/composables/useToast'
import type { Category } from '@/types/api'

const toast = useToast()
const rows = ref<Category[]>([])
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    rows.value = await categoryApi.list()
  } catch (e) {
    error.value = errorMessage(e, 'Gagal memuat kategori')
  } finally {
    loading.value = false
  }
}
onMounted(load)

const columns: Column[] = [
  { key: 'name', label: 'Nama' },
  { key: 'description', label: 'Deskripsi' },
  { key: 'isActive', label: 'Status' },
  { key: 'actions', label: '', align: 'right' },
]

const open = ref(false)
const editing = ref<Category | null>(null)
const form = reactive({ name: '', description: '', isActive: true })
const errors = reactive<Record<string, string>>({})
const saving = ref(false)

function openForm(c: Category | null) {
  editing.value = c
  form.name = c?.name ?? ''
  form.description = c?.description ?? ''
  form.isActive = c?.isActive ?? true
  for (const k of Object.keys(errors)) delete errors[k]
  open.value = true
}

async function save() {
  for (const k of Object.keys(errors)) delete errors[k]
  if (!form.name.trim()) {
    errors.name = 'Nama wajib diisi'
    return
  }
  saving.value = true
  const body = { name: form.name.trim(), description: form.description.trim() || null }
  try {
    if (editing.value) await categoryApi.update(editing.value.id, { ...body, isActive: form.isActive })
    else await categoryApi.create(body)
    toast.success(editing.value ? 'Kategori diperbarui' : 'Kategori dibuat')
    open.value = false
    load()
  } catch (e) {
    if (e instanceof ApiException) Object.assign(errors, e.fieldErrors())
    if (!Object.keys(errors).length) errors.name = errorMessage(e)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <PageHeader title="Kategori" subtitle="Kategori nonaktif tidak muncul di filter aplikasi kasir.">
    <Button @click="openForm(null)"><PlusIcon /> Kategori baru</Button>
  </PageHeader>

  <ErrorAlert v-if="error" :message="error" class="mb-4" />

  <Card class="gap-0 overflow-hidden py-0">
    <DataTable :columns="columns" :rows="rows" :loading="loading" row-key="id" empty="Belum ada kategori">
      <template #cell-name="{ row }"><span class="font-semibold">{{ row.name }}</span></template>
      <template #cell-description="{ row }"><span class="text-muted-foreground">{{ row.description ?? '—' }}</span></template>
      <template #cell-isActive="{ row }"><ActiveBadge :active="row.isActive" /></template>
      <template #cell-actions="{ row }">
        <Button variant="ghost" size="sm" @click="openForm(row)"><SquarePenIcon /> Ubah</Button>
      </template>
    </DataTable>
  </Card>

  <Modal :open="open" :title="editing ? 'Ubah kategori' : 'Kategori baru'" @close="open = false">
    <form class="space-y-4" @submit.prevent="save">
      <FormField label="Nama" for="cat-name" required :error="errors.name">
        <Input id="cat-name" v-model="form.name" :aria-invalid="!!errors.name || undefined" maxlength="60" autofocus />
      </FormField>
      <FormField label="Deskripsi" for="cat-desc" :error="errors.description">
        <Input id="cat-desc" v-model="form.description" maxlength="200" />
      </FormField>
      <div v-if="editing" class="flex items-center gap-3">
        <Switch id="cat-active" v-model="form.isActive" />
        <Label for="cat-active">Aktif</Label>
      </div>
      <DialogFooter class="pt-2">
        <Button type="button" variant="outline" @click="open = false">Batal</Button>
        <Button type="submit" :disabled="saving"><Spinner v-if="saving" /> Simpan</Button>
      </DialogFooter>
    </form>
  </Modal>
</template>
