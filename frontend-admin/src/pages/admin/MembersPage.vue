<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
import FormModal from '@/components/common/FormModal.vue'
import { memberApi } from '@/services/memberApi'
import type { Member } from '@/types/api'

const members = ref<Member[]>([])
const loading = ref(false)
const errorMsg = ref('')

const showForm = ref(false)
const editing = ref<Member | null>(null)
const form = reactive({ memberNumber: '', name: '', phone: '' })
const fieldErrors = reactive<Record<string, string>>({})
const saving = ref(false)

const showConfirm = ref(false)
const toDelete = ref<Member | null>(null)
const deleting = ref(false)

async function load() {
  loading.value = true
  errorMsg.value = ''
  try {
    members.value = await memberApi.list()
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Gagal memuat anggota'
  } finally {
    loading.value = false
  }
}
onMounted(load)

function resetForm() {
  form.memberNumber = ''
  form.name = ''
  form.phone = ''
  Object.keys(fieldErrors).forEach((k) => delete fieldErrors[k])
}

function openCreate() {
  editing.value = null
  resetForm()
  showForm.value = true
}

function openEdit(m: Member) {
  editing.value = m
  form.memberNumber = m.memberNumber
  form.name = m.name
  form.phone = m.phone ?? ''
  Object.keys(fieldErrors).forEach((k) => delete fieldErrors[k])
  showForm.value = true
}

function validate(): boolean {
  Object.keys(fieldErrors).forEach((k) => delete fieldErrors[k])
  if (!form.memberNumber.trim()) fieldErrors.memberNumber = 'Nomor anggota wajib diisi'
  if (!form.name.trim()) fieldErrors.name = 'Nama wajib diisi'
  return Object.keys(fieldErrors).length === 0
}

async function submitForm() {
  if (!validate()) return
  saving.value = true
  try {
    const input = { memberNumber: form.memberNumber.trim(), name: form.name.trim(), phone: form.phone.trim() }
    if (editing.value) {
      await memberApi.update(editing.value.id, input)
    } else {
      await memberApi.create(input)
    }
    showForm.value = false
    await load()
  } catch (e) {
    fieldErrors.memberNumber = e instanceof Error ? e.message : 'Gagal menyimpan anggota'
  } finally {
    saving.value = false
  }
}

function askDelete(m: Member) {
  toDelete.value = m
  showConfirm.value = true
}

async function confirmDelete() {
  if (!toDelete.value) return
  deleting.value = true
  try {
    await memberApi.remove(toDelete.value.id)
    showConfirm.value = false
    await load()
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Gagal menghapus anggota'
    showConfirm.value = false
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-lg font-semibold">Anggota Koperasi</h1>
      <button class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700" @click="openCreate">
        + Anggota Baru
      </button>
    </div>

    <p v-if="errorMsg" class="text-sm text-red-600">{{ errorMsg }}</p>

    <div class="overflow-hidden rounded-xl border bg-white">
      <table class="w-full text-sm">
        <thead class="border-b bg-gray-50 text-left text-gray-500">
          <tr>
            <th class="px-4 py-3 font-medium">No. Anggota</th>
            <th class="px-4 py-3 font-medium">Nama</th>
            <th class="px-4 py-3 font-medium">Telepon</th>
            <th class="px-4 py-3 font-medium">Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="4" class="px-4 py-8 text-center text-gray-400">Memuat data...</td>
          </tr>
          <tr v-else-if="members.length === 0">
            <td colspan="4" class="px-4 py-8 text-center text-gray-400">Belum ada anggota</td>
          </tr>
          <tr v-for="m in members" v-else :key="m.id" class="border-b last:border-0 hover:bg-gray-50">
            <td class="px-4 py-3 font-medium">{{ m.memberNumber }}</td>
            <td class="px-4 py-3">{{ m.name }}</td>
            <td class="px-4 py-3">{{ m.phone || '-' }}</td>
            <td class="px-4 py-3">
              <button class="mr-3 text-blue-600 hover:underline" @click="openEdit(m)">Ubah</button>
              <button class="text-red-600 hover:underline" @click="askDelete(m)">Hapus</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <FormModal :open="showForm" :title="editing ? 'Ubah Anggota' : 'Anggota Baru'" @close="showForm = false">
      <form class="space-y-4" @submit.prevent="submitForm">
        <div>
          <label class="mb-1 block text-sm font-medium">Nomor Anggota</label>
          <input v-model="form.memberNumber" type="text" class="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500" />
          <p v-if="fieldErrors.memberNumber" class="mt-1 text-xs text-red-600">{{ fieldErrors.memberNumber }}</p>
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">Nama</label>
          <input v-model="form.name" type="text" class="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500" />
          <p v-if="fieldErrors.name" class="mt-1 text-xs text-red-600">{{ fieldErrors.name }}</p>
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">Telepon</label>
          <input v-model="form.phone" type="text" class="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500" />
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
      title="Hapus anggota?"
      :message="`Anggota '${toDelete?.name}' akan dihapus.`"
      confirm-text="Hapus"
      danger
      @confirm="confirmDelete"
      @cancel="showConfirm = false"
    />
  </div>
</template>