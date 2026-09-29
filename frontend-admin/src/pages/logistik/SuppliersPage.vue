<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
import FormModal from '@/components/common/FormModal.vue'
import { supplierApi } from '@/services/supplierApi'
import type { Supplier } from '@/types/api'

const suppliers = ref<Supplier[]>([])
const loading = ref(false)
const errorMsg = ref('')

const showForm = ref(false)
const editing = ref<Supplier | null>(null)
const form = reactive({ name: '', phone: '', address: '' })
const fieldErrors = reactive<Record<string, string>>({})
const saving = ref(false)

const showConfirm = ref(false)
const toDelete = ref<Supplier | null>(null)
const deleting = ref(false)

async function load() {
  loading.value = true
  errorMsg.value = ''
  try {
    suppliers.value = await supplierApi.list()
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Gagal memuat supplier'
  } finally {
    loading.value = false
  }
}
onMounted(load)

function resetForm() {
  form.name = ''
  form.phone = ''
  form.address = ''
  Object.keys(fieldErrors).forEach((k) => delete fieldErrors[k])
}

function openCreate() {
  editing.value = null
  resetForm()
  showForm.value = true
}

function openEdit(s: Supplier) {
  editing.value = s
  form.name = s.name
  form.phone = s.phone ?? ''
  form.address = s.address ?? ''
  Object.keys(fieldErrors).forEach((k) => delete fieldErrors[k])
  showForm.value = true
}

function validate(): boolean {
  Object.keys(fieldErrors).forEach((k) => delete fieldErrors[k])
  if (!form.name.trim()) fieldErrors.name = 'Nama supplier wajib diisi'
  return Object.keys(fieldErrors).length === 0
}

async function submitForm() {
  if (!validate()) return
  saving.value = true
  try {
    const input = { name: form.name.trim(), phone: form.phone.trim(), address: form.address.trim() }
    if (editing.value) {
      await supplierApi.update(editing.value.id, input)
    } else {
      await supplierApi.create(input)
    }
    showForm.value = false
    await load()
  } catch (e) {
    fieldErrors.name = e instanceof Error ? e.message : 'Gagal menyimpan supplier'
  } finally {
    saving.value = false
  }
}

function askDelete(s: Supplier) {
  toDelete.value = s
  showConfirm.value = true
}

async function confirmDelete() {
  if (!toDelete.value) return
  deleting.value = true
  try {
    await supplierApi.remove(toDelete.value.id)
    showConfirm.value = false
    await load()
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Gagal menghapus supplier'
    showConfirm.value = false
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-lg font-semibold">Supplier</h1>
      <button class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700" @click="openCreate">
        + Supplier Baru
      </button>
    </div>

    <p v-if="errorMsg" class="text-sm text-red-600">{{ errorMsg }}</p>

    <div class="overflow-hidden rounded-xl border bg-white">
      <table class="w-full text-sm">
        <thead class="border-b bg-gray-50 text-left text-gray-500">
          <tr>
            <th class="px-4 py-3 font-medium">Nama</th>
            <th class="px-4 py-3 font-medium">Telepon</th>
            <th class="px-4 py-3 font-medium">Alamat</th>
            <th class="px-4 py-3 font-medium">Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="4" class="px-4 py-8 text-center text-gray-400">Memuat data...</td>
          </tr>
          <tr v-else-if="suppliers.length === 0">
            <td colspan="4" class="px-4 py-8 text-center text-gray-400">Belum ada supplier</td>
          </tr>
          <tr v-for="s in suppliers" v-else :key="s.id" class="border-b last:border-0 hover:bg-gray-50">
            <td class="px-4 py-3">{{ s.name }}</td>
            <td class="px-4 py-3">{{ s.phone || '-' }}</td>
            <td class="px-4 py-3">{{ s.address || '-' }}</td>
            <td class="px-4 py-3">
              <button class="mr-3 text-blue-600 hover:underline" @click="openEdit(s)">Ubah</button>
              <button class="text-red-600 hover:underline" @click="askDelete(s)">Hapus</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <FormModal :open="showForm" :title="editing ? 'Ubah Supplier' : 'Supplier Baru'" @close="showForm = false">
      <form class="space-y-4" @submit.prevent="submitForm">
        <div>
          <label class="mb-1 block text-sm font-medium">Nama Supplier</label>
          <input v-model="form.name" type="text" class="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500" />
          <p v-if="fieldErrors.name" class="mt-1 text-xs text-red-600">{{ fieldErrors.name }}</p>
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">Telepon</label>
          <input v-model="form.phone" type="text" class="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">Alamat</label>
          <textarea v-model="form.address" rows="2" class="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"></textarea>
        </div>
        <div class="flex justify-end gap-3">
          <button type="button" class="rounded-lg border px-4 py-2 text-sm hover:bg-gray-50" @click="showForm = false">
            Batal
          </button>
          <button type="submit" :disabled="saving"
            class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
            {{ saving ? 'Menyimpan...' : 'Simpan' }}
          </button>
        </div>
      </form>
    </FormModal>

    <ConfirmModal
      :open="showConfirm"
      title="Hapus supplier?"
      :message="`Supplier '${toDelete?.name}' akan dihapus.`"
      confirm-text="Hapus"
      danger
      @confirm="confirmDelete"
      @cancel="showConfirm = false"
    />
  </div>
</template>