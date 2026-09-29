<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
import FormModal from '@/components/common/FormModal.vue'
import { categoryApi } from '@/services/categoryApi'
import type { Category } from '@/types/api'

const categories = ref<Category[]>([])
const loading = ref(false)
const errorMsg = ref('')

// state modal form (tambah/ubah)
const showForm = ref(false)
const editing = ref<Category | null>(null)
const form = reactive({ name: '' })
const fieldError = ref('')
const saving = ref(false)

// state modal hapus
const showConfirm = ref(false)
const toDelete = ref<Category | null>(null)
const deleting = ref(false)

async function load() {
  loading.value = true
  errorMsg.value = ''
  try {
    categories.value = await categoryApi.list()
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Gagal memuat kategori'
  } finally {
    loading.value = false
  }
}
onMounted(load)

function openCreate() {
  editing.value = null
  form.name = ''
  fieldError.value = ''
  showForm.value = true
}

function openEdit(cat: Category) {
  editing.value = cat
  form.name = cat.name
  fieldError.value = ''
  showForm.value = true
}

async function submitForm() {
  if (!form.name.trim()) {
    fieldError.value = 'Nama kategori wajib diisi'
    return
  }
  saving.value = true
  try {
    if (editing.value) {
      await categoryApi.update(editing.value.id, form.name.trim())
    } else {
      await categoryApi.create(form.name.trim())
    }
    showForm.value = false
    await load()
  } catch (e) {
    fieldError.value = e instanceof Error ? e.message : 'Gagal menyimpan kategori'
  } finally {
    saving.value = false
  }
}

function askDelete(cat: Category) {
  toDelete.value = cat
  showConfirm.value = true
}

async function confirmDelete() {
  if (!toDelete.value) return
  deleting.value = true
  try {
    await categoryApi.remove(toDelete.value.id)
    showConfirm.value = false
    await load()
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Gagal menghapus kategori'
    showConfirm.value = false
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-lg font-semibold">Kategori</h1>
      <button class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700" @click="openCreate">
        + Kategori Baru
      </button>
    </div>

    <p v-if="errorMsg" class="text-sm text-red-600">{{ errorMsg }}</p>

    <div class="overflow-hidden rounded-xl border bg-white">
      <table class="w-full text-sm">
        <thead class="border-b bg-gray-50 text-left text-gray-500">
          <tr>
            <th class="px-4 py-3 font-medium">Nama</th>
            <th class="px-4 py-3 font-medium">Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="2" class="px-4 py-8 text-center text-gray-400">Memuat data...</td>
          </tr>
          <tr v-else-if="categories.length === 0">
            <td colspan="2" class="px-4 py-8 text-center text-gray-400">Belum ada kategori</td>
          </tr>
          <tr v-for="c in categories" v-else :key="c.id" class="border-b last:border-0 hover:bg-gray-50">
            <td class="px-4 py-3">{{ c.name }}</td>
            <td class="px-4 py-3">
              <button class="mr-3 text-blue-600 hover:underline" @click="openEdit(c)">Ubah</button>
              <button class="text-red-600 hover:underline" @click="askDelete(c)">Hapus</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <FormModal :open="showForm" :title="editing ? 'Ubah Kategori' : 'Kategori Baru'" @close="showForm = false">
      <form class="space-y-4" @submit.prevent="submitForm">
        <div>
          <label class="mb-1 block text-sm font-medium">Nama Kategori</label>
          <input v-model="form.name" type="text" class="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500" />
          <p v-if="fieldError" class="mt-1 text-xs text-red-600">{{ fieldError }}</p>
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
      title="Hapus kategori?"
      :message="`Kategori '${toDelete?.name}' akan dihapus.`"
      confirm-text="Hapus"
      danger
      @confirm="confirmDelete"
      @cancel="showConfirm = false"
    />
  </div>
</template>