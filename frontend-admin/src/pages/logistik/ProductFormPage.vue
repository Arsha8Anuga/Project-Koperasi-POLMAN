<script setup lang="ts">
import { ArrowLeftIcon } from '@lucide/vue'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import FormField from '@/components/form/FormField.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { NativeSelect, NativeSelectOption } from '@/components/ui/native-select'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import { Spinner } from '@/components/ui/spinner'
import { categoryApi, productApi } from '@/services/api'
import { ApiException, errorMessage } from '@/services/apiClient'
import { useToast } from '@/composables/useToast'
import type { Category, Product, ProductInput } from '@/types/api'
import { formatRupiah } from '@/utils/format'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const id = computed(() => (route.params.id ? String(route.params.id) : null))
const categories = ref<Category[]>([])
const product = ref<Product | null>(null)
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const errors = reactive<Record<string, string>>({})

const form = reactive({
  sku: '',
  barcode: '',
  name: '',
  categoryId: '',
  unit: 'pcs',
  sellingPrice: 0,
  minimumStock: 0,
  imageUrl: '',
})

onMounted(async () => {
  try {
    categories.value = await categoryApi.list(true)
    if (id.value) {
      product.value = await productApi.get(id.value)
      const p = product.value
      Object.assign(form, {
        sku: p.sku,
        barcode: p.barcode ?? '',
        name: p.name,
        categoryId: p.categoryId,
        unit: p.unit,
        sellingPrice: p.sellingPrice,
        minimumStock: p.minimumStock,
        imageUrl: p.imageUrl ?? '',
      })
      // kategori produk mungkin sudah nonaktif: tetap tampilkan supaya select tidak kosong
      if (!categories.value.some((c) => c.id === p.categoryId) && p.categoryName) {
        categories.value.push({ id: p.categoryId, name: `${p.categoryName} (nonaktif)`, description: null, isActive: false })
      }
    }
  } catch (e) {
    error.value = errorMessage(e, 'Gagal memuat data')
  } finally {
    loading.value = false
  }
})

function validate(): boolean {
  for (const k of Object.keys(errors)) delete errors[k]
  if (!form.sku.trim()) errors.sku = 'SKU wajib diisi'
  if (!form.name.trim()) errors.name = 'Nama wajib diisi'
  if (!form.categoryId) errors.categoryId = 'Pilih kategori'
  if (!form.unit.trim()) errors.unit = 'Satuan wajib diisi'
  if (!Number.isInteger(form.sellingPrice) || form.sellingPrice < 0) errors.sellingPrice = 'Harga harus bilangan bulat ≥ 0'
  if (!Number.isInteger(form.minimumStock) || form.minimumStock < 0) errors.minimumStock = 'Harus bilangan bulat ≥ 0'
  return Object.keys(errors).length === 0
}

async function submit() {
  if (!validate()) return
  saving.value = true
  error.value = ''
  const body: ProductInput = {
    sku: form.sku.trim(),
    barcode: form.barcode.trim() || null,
    name: form.name.trim(),
    categoryId: form.categoryId,
    unit: form.unit.trim(),
    sellingPrice: form.sellingPrice,
    minimumStock: form.minimumStock,
    imageUrl: form.imageUrl.trim() || null,
  }
  try {
    const saved = id.value ? await productApi.update(id.value, body) : await productApi.create(body)
    toast.success(id.value ? 'Produk diperbarui' : `Produk ${saved.sku} dibuat`)
    router.push({ name: 'products' })
  } catch (e) {
    if (e instanceof ApiException) Object.assign(errors, e.fieldErrors())
    error.value = errorMessage(e, 'Gagal menyimpan produk')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <Button as-child variant="ghost" size="sm" class="mb-4 -ml-2">
    <RouterLink :to="{ name: 'products' }"><ArrowLeftIcon /> Produk</RouterLink>
  </Button>
  <h1 class="mb-6 text-2xl font-bold tracking-tight">{{ id ? 'Ubah produk' : 'Produk baru' }}</h1>

  <div v-if="loading" class="grid gap-6 lg:grid-cols-[1fr_18rem]">
    <Skeleton class="h-[30rem] rounded-xl" />
    <Skeleton class="h-48 rounded-xl" />
  </div>

  <div v-else class="grid items-start gap-6 lg:grid-cols-[1fr_18rem]">
    <Card>
      <form novalidate @submit.prevent="submit">
        <CardContent class="space-y-5">
          <ErrorAlert v-if="error" :message="error" />

          <div class="grid gap-5 sm:grid-cols-2">
            <FormField label="SKU" for="sku" required :error="errors.sku" hint="Kode unik, otomatis huruf besar">
              <Input id="sku" v-model="form.sku" class="font-mono uppercase" :aria-invalid="!!errors.sku || undefined" maxlength="40" />
            </FormField>
            <FormField label="Barcode" for="barcode" :error="errors.barcode" hint="Opsional">
              <Input id="barcode" v-model="form.barcode" class="font-mono" :aria-invalid="!!errors.barcode || undefined" maxlength="40" />
            </FormField>
          </div>
          <FormField label="Nama produk" for="name" required :error="errors.name">
            <Input id="name" v-model="form.name" :aria-invalid="!!errors.name || undefined" maxlength="120" />
          </FormField>
          <div class="grid gap-5 sm:grid-cols-2">
            <FormField label="Kategori" for="category" required :error="errors.categoryId">
              <NativeSelect id="category" v-model="form.categoryId" class="w-full" :aria-invalid="!!errors.categoryId || undefined">
                <NativeSelectOption value="" disabled>Pilih kategori</NativeSelectOption>
                <NativeSelectOption v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</NativeSelectOption>
              </NativeSelect>
            </FormField>
            <FormField label="Satuan" for="unit" required :error="errors.unit" hint="pcs, botol, kg, …">
              <Input id="unit" v-model="form.unit" :aria-invalid="!!errors.unit || undefined" maxlength="20" />
            </FormField>
          </div>
          <div class="grid gap-5 sm:grid-cols-2">
            <FormField label="Harga jual (Rp)" for="price" required :error="errors.sellingPrice">
              <Input
                id="price"
                v-model.number="form.sellingPrice"
                type="number"
                min="0"
                step="1"
                class="num"
                :aria-invalid="!!errors.sellingPrice || undefined"
              />
            </FormField>
            <FormField label="Stok minimum" for="min" required :error="errors.minimumStock" hint="Di bawah angka ini stok dianggap menipis">
              <Input
                id="min"
                v-model.number="form.minimumStock"
                type="number"
                min="0"
                step="1"
                class="num"
                :aria-invalid="!!errors.minimumStock || undefined"
              />
            </FormField>
          </div>
          <FormField label="URL gambar" for="image" :error="errors.imageUrl" hint="Opsional">
            <Input id="image" v-model="form.imageUrl" type="url" placeholder="https://…" :aria-invalid="!!errors.imageUrl || undefined" />
          </FormField>
        </CardContent>
        <Separator class="my-6" />
        <CardFooter class="gap-2">
          <Button type="submit" :disabled="saving"><Spinner v-if="saving" /> Simpan</Button>
          <Button as-child variant="outline"><RouterLink :to="{ name: 'products' }">Batal</RouterLink></Button>
        </CardFooter>
      </form>
    </Card>

    <Card class="text-sm">
      <CardHeader>
        <CardTitle class="text-base">Stok & HPP</CardTitle>
        <CardDescription>Diperbarui otomatis setiap restock.</CardDescription>
      </CardHeader>
      <CardContent class="space-y-3">
        <template v-if="product">
          <div class="flex justify-between">
            <span class="text-muted-foreground">Stok saat ini</span>
            <span class="num font-semibold">{{ product.stock }} {{ product.unit }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-muted-foreground">HPP rata-rata</span>
            <span class="num font-semibold">{{ formatRupiah(product.costPrice) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-muted-foreground">Harga beli terakhir</span>
            <span class="num font-semibold">{{ formatRupiah(product.lastPurchasePrice) }}</span>
          </div>
          <Separator />
        </template>
        <p class="text-muted-foreground">
          Stok, HPP, dan harga beli <strong class="text-foreground">tidak bisa diubah di sini</strong>. HPP dihitung sebagai
          rata-rata bergerak dari setiap restock.
        </p>
      </CardContent>
    </Card>
  </div>
</template>
