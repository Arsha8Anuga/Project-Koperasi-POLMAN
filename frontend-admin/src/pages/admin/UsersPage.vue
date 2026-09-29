<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
import FormModal from '@/components/common/FormModal.vue'
import { userApi } from '@/services/userApi'
import type { AdminUser, Role } from '@/types/api'

const users = ref<AdminUser[]>([])
const loading = ref(false)
const errorMsg = ref('')

const roles: Role[] = ['OWNER', 'LOGISTIK', 'ADMIN', 'KASIR']

const showForm = ref(false)
const editing = ref<AdminUser | null>(null)
const form = reactive({ name: '', username: '', role: 'KASIR' as Role, password: '' })
const fieldErrors = reactive<Record<string, string>>({})
const saving = ref(false)

const showConfirm = ref(false)
const toToggle = ref<AdminUser | null>(null)
const toggling = ref(false)

async function load() {
  loading.value = true
  errorMsg.value = ''
  try {
    users.value = await userApi.list()
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Gagal memuat user'
  } finally {
    loading.value = false
  }
}
onMounted(load)

function resetForm() {
  form.name = ''
  form.username = ''
  form.role = 'KASIR'
  form.password = ''
  Object.keys(fieldErrors).forEach((k) => delete fieldErrors[k])
}

function openCreate() {
  editing.value = null
  resetForm()
  showForm.value = true
}

function openEdit(u: AdminUser) {
  editing.value = u
  form.name = u.name
  form.username = u.username
  form.role = u.role
  form.password = ''
  Object.keys(fieldErrors).forEach((k) => delete fieldErrors[k])
  showForm.value = true
}

function validate(): boolean {
  Object.keys(fieldErrors).forEach((k) => delete fieldErrors[k])
  if (!form.name.trim()) fieldErrors.name = 'Nama wajib diisi'
  if (!form.username.trim()) fieldErrors.username = 'Username wajib diisi'
  if (!editing.value && !form.password.trim()) fieldErrors.password = 'Password wajib diisi untuk user baru'
  return Object.keys(fieldErrors).length === 0
}

async function submitForm() {
  if (!validate()) return
  saving.value = true
  try {
    const input = { name: form.name.trim(), username: form.username.trim(), role: form.role, password: form.password || undefined }
    if (editing.value) {
      await userApi.update(editing.value.id, input)
    } else {
      await userApi.create(input)
    }
    showForm.value = false
    await load()
  } catch (e) {
    fieldErrors.username = e instanceof Error ? e.message : 'Gagal menyimpan user'
  } finally {
    saving.value = false
  }
}

function askToggle(u: AdminUser) {
  toToggle.value = u
  showConfirm.value = true
}

async function confirmToggle() {
  if (!toToggle.value) return
  toggling.value = true
  try {
    await userApi.toggleActive(toToggle.value.id)
    showConfirm.value = false
    await load()
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Gagal mengubah status user'
    showConfirm.value = false
  } finally {
    toggling.value = false
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-lg font-semibold">User Management</h1>
      <button class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700" @click="openCreate">
        + User Baru
      </button>
    </div>

    <p v-if="errorMsg" class="text-sm text-red-600">{{ errorMsg }}</p>

    <div class="overflow-hidden rounded-xl border bg-white">
      <table class="w-full text-sm">
        <thead class="border-b bg-gray-50 text-left text-gray-500">
          <tr>
            <th class="px-4 py-3 font-medium">Nama</th>
            <th class="px-4 py-3 font-medium">Username</th>
            <th class="px-4 py-3 font-medium">Role</th>
            <th class="px-4 py-3 font-medium">Status</th>
            <th class="px-4 py-3 font-medium">Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="5" class="px-4 py-8 text-center text-gray-400">Memuat data...</td>
          </tr>
          <tr v-else-if="users.length === 0">
            <td colspan="5" class="px-4 py-8 text-center text-gray-400">Belum ada user</td>
          </tr>
          <tr v-for="u in users" v-else :key="u.id" class="border-b last:border-0 hover:bg-gray-50">
            <td class="px-4 py-3">{{ u.name }}</td>
            <td class="px-4 py-3">{{ u.username }}</td>
            <td class="px-4 py-3">
              <span class="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700">{{ u.role }}</span>
            </td>
            <td class="px-4 py-3">
              <span class="rounded-full px-2 py-0.5 text-xs font-medium" :class="u.isActive ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">
                {{ u.isActive ? 'Aktif' : 'Nonaktif' }}
              </span>
            </td>
            <td class="px-4 py-3">
              <button class="mr-3 text-blue-600 hover:underline" @click="openEdit(u)">Ubah</button>
              <button class="text-amber-600 hover:underline" @click="askToggle(u)">
                {{ u.isActive ? 'Nonaktifkan' : 'Aktifkan' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <FormModal :open="showForm" :title="editing ? 'Ubah User' : 'User Baru'" @close="showForm = false">
      <form class="space-y-4" @submit.prevent="submitForm">
        <div>
          <label class="mb-1 block text-sm font-medium">Nama</label>
          <input v-model="form.name" type="text" class="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500" />
          <p v-if="fieldErrors.name" class="mt-1 text-xs text-red-600">{{ fieldErrors.name }}</p>
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">Username</label>
          <input v-model="form.username" type="text" class="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500" />
          <p v-if="fieldErrors.username" class="mt-1 text-xs text-red-600">{{ fieldErrors.username }}</p>
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">Role</label>
          <select v-model="form.role" class="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500">
            <option v-for="r in roles" :key="r" :value="r">{{ r }}</option>
          </select>
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">
            Password {{ editing ? '(kosongkan jika tidak diubah)' : '' }}
          </label>
          <input v-model="form.password" type="password" class="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500" />
          <p v-if="fieldErrors.password" class="mt-1 text-xs text-red-600">{{ fieldErrors.password }}</p>
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
      :title="toToggle?.isActive ? 'Nonaktifkan user?' : 'Aktifkan user?'"
      :message="`User '${toToggle?.name}' akan ${toToggle?.isActive ? 'dinonaktifkan' : 'diaktifkan'}.`"
      :confirm-text="toToggle?.isActive ? 'Nonaktifkan' : 'Aktifkan'"
      :danger="toToggle?.isActive"
      @confirm="confirmToggle"
      @cancel="showConfirm = false"
    />
  </div>
</template>