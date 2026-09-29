<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import FormField from '@/components/form/FormField.vue'
import { categoryApi } from '@/services/categoryApi'
import { productApi } from '@/services/productApi'
import type { Category } from '@/types/api'

const route = useRoute()
const router = useRouter()
const id = route.params.id as string | undefined
const isEdit = !!id

const categories = ref<Category[]>([])
const loading = ref(false)
const saving = ref(false)
const errorMsg = ref('')
const fieldErrors = reactive<Record<string, string>>({})

const form = reactive({
  sku: '',
  name: '',
  categoryId: '',
  sellPrice: 0,
  minimumStock: 0,
})

function validate(): boolean {
  Object.keys(fieldErrors).forEach((k) => delete fieldErrors[k])
  if (!form.sku) fieldErrors.sku = 'SKU wajib diisi'
  if (!form.name) fieldErrors.name = 'Nama wajib diisi'
  if (!form.categoryId) fieldErrors.categoryId = 'Kategori wajib dipilih'
  if (form.sellPrice < 0) fieldErrors.sellPrice = 'Harga tidak boleh negatif'
  if (form.minimumStock < 0) fieldErrors.minimumStock = 'Stok minimum tidak boleh negatif'
  return Object.keys(fieldErrors).length === 0
}

async function submit() {
  if (!validate()) return
  saving.value = true
  errorMsg.value = ''
  try {
    if (isEdit && id) {
      await productApi.update(id, { ...form })
    } else {
      await productApi.create({ ...form })
    }
    router.push('/logistik/products')
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Gagal menyimpan produk'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  categories.value = await categoryApi.list()
  if (isEdit && id) {
    loading.value = true
    try {
      const p = await productApi.get(id)
      form.sku = p.sku
      form.name = p.name
      form.categoryId = p.categoryId
      form.sellPrice = p.sellPrice
      form.minimumStock = p.minimumStock
    } catch (e) {
      errorMsg.value = e instanceof Error ? e.message : 'Gagal memuat produk'
    } finally {
      loading.value = false
    }
  }
})
</script>

<template>
  <div class="max-w-xl">
    <h1 class="mb-4 text-lg font-semibold">{{ isEdit ? 'Ubah Produk' : 'Produk Baru' }}</h1>

    <p v-if="loading" class="text-sm text-gray-400">Memuat data...</p>

    <form v-else class="space-y-4 rounded-xl border bg-white p-6" @submit.prevent="submit">
      <FormField label="SKU" required :error="fieldErrors.sku">
        <input v-model="form.sku" type="text" class="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500" />
      </FormField>

      <FormField label="Nama Produk" required :error="fieldErrors.name">
        <input v-model="form.name" type="text" class="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500" />
      </FormField>

      <FormField label="Kategori" required :error="fieldErrors.categoryId">
        <select v-model="form.categoryId" class="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500">
          <option value="" disabled>Pilih kategori</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </FormField>

      <FormField label="Harga Jual" required :error="fieldErrors.sellPrice">
        <input v-model.number="form.sellPrice" type="number" min="0" class="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500" />
      </FormField>

      <FormField label="Stok Minimum" required :error="fieldErrors.minimumStock">
        <input v-model.number="form.minimumStock" type="number" min="0" class="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500" />
      </FormField>

      <p v-if="errorMsg" class="text-sm text-red-600">{{ errorMsg }}</p>

      <div class="flex gap-3">
        <button type="submit" :disabled="saving"
          class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
          {{ saving ? 'Menyimpan...' : 'Simpan' }}
        </button>
        <RouterLink to="/logistik/products" class="rounded-lg border px-4 py-2 text-sm hover:bg-gray-50">
          Batal
        </RouterLink>
      </div>
    </form>
  </div>
</template>