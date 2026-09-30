<script setup lang="ts">
import { ArrowLeftIcon, BanknoteIcon, CircleAlertIcon, QrCodeIcon, ShoppingCartIcon } from '@lucide/vue'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import CashPanel from '@/components/payment/CashPanel.vue'
import MemberLookup from '@/components/payment/MemberLookup.vue'
import QrisPanel from '@/components/payment/QrisPanel.vue'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Empty, EmptyContent, EmptyHeader, EmptyMedia, EmptyTitle } from '@/components/ui/empty'
import { Field, FieldLabel } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import { ApiException, errorMessage } from '@/services/api'
import { salesApi } from '@/services/salesApi'
import { useCartStore } from '@/stores/cart'
import type { MemberLookup as Member, PaymentMethod, SaleRequest, StockIssue } from '@/types'
import { formatRupiah } from '@/utils/format'
import ProductImage from '@/components/product/ProductImage.vue'

const cart = useCartStore()
const router = useRouter()

const method = ref<PaymentMethod>('CASH')
const member = ref<Member | null>(null)
const customerName = ref('')
const submitting = ref(false)
const error = ref('')
const issues = ref<StockIssue[]>([])

const total = computed(() => cart.totalAmount)

/** ToggleGroup mengirim undefined kalau item aktif diklik lagi — abaikan supaya selalu ada metode. */
function setMethod(v: unknown) {
  if (v === 'CASH' || v === 'QRIS') method.value = v
}

async function pay(amountPaid?: number) {
  if (submitting.value || cart.isEmpty) return
  submitting.value = true
  error.value = ''
  issues.value = []
  const body: SaleRequest = {
    items: cart.items.map((i) => ({ productId: i.productId, quantity: i.quantity })),
    customerName: customerName.value.trim() || null,
    memberId: member.value?.id ?? null,
    payment: method.value === 'CASH' ? { method: 'CASH', amountPaid: amountPaid ?? 0 } : { method: 'QRIS' },
  }
  try {
    const sale = await salesApi.create(body)
    cart.clear()
    router.replace({ name: 'invoice', params: { id: sale.id }, query: { new: '1' } })
  } catch (e) {
    error.value = errorMessage(e, 'Transaksi gagal')
    if (e instanceof ApiException && ['INSUFFICIENT_STOCK', 'PRODUCT_INACTIVE', 'NOT_FOUND'].includes(e.code ?? '')) {
      issues.value = e.details as StockIssue[]
    }
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="h-full overflow-y-auto">
    <div class="mx-auto max-w-5xl px-4 py-6 sm:px-6">
      <div class="mb-6 flex items-center gap-3">
        <Button as-child variant="ghost" size="icon" aria-label="Kembali ke kasir">
          <RouterLink :to="{ name: 'pos' }"><ArrowLeftIcon class="size-5" /></RouterLink>
        </Button>
        <div>
          <h1 class="text-2xl font-bold">Pembayaran</h1>
          <p class="text-sm text-muted-foreground">Periksa pesanan, lalu pilih metode pembayaran.</p>
        </div>
      </div>

      <Card v-if="cart.isEmpty">
        <Empty>
          <EmptyHeader>
            <EmptyMedia variant="icon"><ShoppingCartIcon /></EmptyMedia>
            <EmptyTitle>Keranjang kosong</EmptyTitle>
          </EmptyHeader>
          <EmptyContent>
            <Button as-child size="sm"><RouterLink :to="{ name: 'pos' }">Kembali ke kasir</RouterLink></Button>
          </EmptyContent>
        </Empty>
      </Card>

      <div v-else class="grid items-start gap-6 lg:grid-cols-[1fr_26rem]">
        <Card class="gap-0 rounded-2xl py-0">
          <CardHeader class="flex items-center justify-between border-b pt-4 pb-4!">
            <CardTitle>Ringkasan pesanan</CardTitle>
            <Badge variant="soft">{{ cart.totalQty }} barang</Badge>
          </CardHeader>
          <CardContent>
            <ul class="divide-y">
              <li v-for="item in cart.items" :key="item.productId" class="flex items-center gap-3 py-3">
                <ProductImage :src="item.imageUrl" :name="item.name" class="size-11 shrink-0 rounded-lg" text-class="text-xs" />
                <div class="min-w-0 flex-1">
                  <p class="truncate text-sm font-semibold">{{ item.name }}</p>
                  <p class="num text-xs text-muted-foreground">{{ item.quantity }} × {{ formatRupiah(item.price) }}</p>
                </div>
                <p class="num text-sm font-semibold">{{ formatRupiah(item.price * item.quantity) }}</p>
              </li>
            </ul>
          </CardContent>
          <CardFooter class="flex-col items-stretch gap-4 rounded-b-xl border-t bg-muted/50 pt-4! pb-4">
            <div class="grid gap-4 sm:grid-cols-2">
              <Field>
                <FieldLabel for="customer">
                  Nama pelanggan <span class="font-normal text-muted-foreground">(opsional)</span>
                </FieldLabel>
                <Input id="customer" v-model="customerName" maxlength="60" placeholder="contoh: Budi" class="bg-background" />
              </Field>
              <MemberLookup v-model="member" />
            </div>
            <div class="flex items-baseline justify-between">
              <span class="font-semibold text-muted-foreground">Total bayar</span>
              <span class="num text-3xl font-extrabold tracking-tight">{{ formatRupiah(total) }}</span>
            </div>
          </CardFooter>
        </Card>

        <Card>
          <CardContent class="space-y-5">
            <ToggleGroup
              type="single"
              variant="outline"
              class="grid w-full grid-cols-2"
              :model-value="method"
              aria-label="Metode pembayaran"
              @update:model-value="setMethod"
            >
              <ToggleGroupItem value="CASH" class="h-10 font-semibold"><BanknoteIcon /> Tunai</ToggleGroupItem>
              <ToggleGroupItem value="QRIS" class="h-10 font-semibold"><QrCodeIcon /> QRIS</ToggleGroupItem>
            </ToggleGroup>

            <Alert v-if="error" variant="destructive">
              <CircleAlertIcon />
              <AlertTitle class="line-clamp-none">{{ error }}</AlertTitle>
              <AlertDescription v-if="issues.length">
                <ul class="space-y-0.5">
                  <li v-for="(it, i) in issues" :key="i">
                    {{ it.name ?? 'Produk' }}<template v-if="it.available !== undefined">
                      — diminta {{ it.requested }}, tersedia {{ it.available }}</template
                    >
                  </li>
                </ul>
                <RouterLink :to="{ name: 'pos' }" class="mt-1 inline-block font-semibold underline">Ubah keranjang</RouterLink>
              </AlertDescription>
            </Alert>

            <CashPanel v-if="method === 'CASH'" :total="total" :loading="submitting" @submit="pay" />
            <QrisPanel v-else :total="total" :loading="submitting" @confirm="pay()" />
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
</template>
