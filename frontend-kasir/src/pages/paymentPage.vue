<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import CashPanel from '../components/payment/CashPanel.vue'
import QrisPanel from '../components/payment/QrisPanel.vue'
import MemberLookup from '../components/payment/MemberLookup.vue'
import { formatRupiah } from '../utils/formatRupiah'
import { memberApi } from '../services/memberApi'
import { salesApi } from '../services/salesApi'
import { useCartStore } from '../stores/cart'
import type { SaleRequest } from '../types/sale'
import type { PaymentMethod } from '../types/transaction'
import type { MemberLookupResult } from '../types/member'

const router = useRouter()
const cart = useCartStore()

const cartItems = computed(() => cart.items)
const total = computed(() => cart.totalAmount)

const method = ref<PaymentMethod>('CASH')

const member = ref<MemberLookupResult | null>(null)
const memberLoading = ref(false)
const memberError = ref('')

async function onCheckMember(memberNumber: string) {
  memberLoading.value = true
  memberError.value = ''
  try {
    member.value = await memberApi.lookup(memberNumber)
  } catch (e) {
    member.value = null
    memberError.value = e instanceof Error ? e.message : 'Terjadi kesalahan'
  } finally {
    memberLoading.value = false
  }
}
function onClearMember() {
  member.value = null
  memberError.value = ''
}

const submitting = ref(false)
const submitError = ref('')

async function pay(amountPaid?: number) {
  if (submitting.value) return
  submitting.value = true
  submitError.value = ''
  try {
    const req: SaleRequest = {
      items: cartItems.value.map((i) => ({ productId: i.productId, quantity: i.quantity })),
      customerName: member.value ? member.value.name : null,
      memberId: member.value ? member.value.id : null,
      payment: method.value === 'CASH' ? { method: 'CASH', amountPaid } : { method: 'QRIS' },
    }
    const tx = await salesApi.create(req)
    cart.clearCart()
    router.push(`/invoice/${tx.id}`)
  } catch (e) {
    submitError.value = e instanceof Error ? e.message : 'Terjadi kesalahan'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-md px-4 py-6">
    <h2 class="text-lg font-bold text-slate-900">Pembayaran</h2>

    <div class="mt-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div v-for="item in cartItems" :key="item.productId" class="flex justify-between py-1 text-sm text-slate-600">
        <span>{{ item.name }} ({{ item.quantity }} × {{ formatRupiah(item.price) }})</span>
        <span class="font-medium text-slate-800">{{ formatRupiah(item.price * item.quantity) }}</span>
      </div>
      <div class="mt-2 flex justify-between border-t border-slate-100 pt-2 text-sm font-bold text-slate-900">
        <span>Total</span>
        <span>{{ formatRupiah(total) }}</span>
      </div>
    </div>

    <div class="mt-4">
      <MemberLookup
        :member="member" :loading="memberLoading" :error="memberError"
        @check="onCheckMember" @clear="onClearMember"
      />
    </div>

    <div class="mt-4 flex justify-center gap-6">
      <label class="flex items-center gap-2 text-sm font-medium text-slate-700">
        <input v-model="method" type="radio" value="CASH" class="accent-indigo-600" /> Tunai
      </label>
      <label class="flex items-center gap-2 text-sm font-medium text-slate-700">
        <input v-model="method" type="radio" value="QRIS" class="accent-indigo-600" /> QRIS
      </label>
    </div>

    <div class="mt-4">
      <CashPanel v-if="method === 'CASH'" :total="total" :loading="submitting" @submit="pay" />
      <QrisPanel v-else :total="total" :loading="submitting" @confirm="pay()" />
    </div>

    <p v-if="submitError" class="mt-3 text-center text-sm font-medium text-rose-500">{{ submitError }}</p>
  </div>
</template>