<script setup lang="ts">
import { useCartStore } from '../../stores/cart';

const cartStore = useCartStore();

const formatRupiah = (val: number) => {
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(val);
};
</script>

<template>
  <div class="bg-white border-l border-gray-200 h-full flex flex-col justify-between p-4 shadow-lg">
    <div>
      <div class="flex justify-between items-center pb-4 mb-4 border-b">
        <h2 class="text-lg font-bold text-gray-800">Keranjang Belanja</h2>
        <button 
          @click="cartStore.clearCart" 
          v-if="cartStore.items.length > 0"
          class="text-xs text-red-500 hover:underline"
        >
          Kosongkan
        </button>
      </div>

      <!-- List Items -->
      <div v-if="cartStore.items.length === 0" class="text-center py-12 text-gray-400">
        <p class="text-sm">Keranjang masih kosong</p>
      </div>

      <div v-else class="space-y-3 max-h-[calc(100vh-280px)] overflow-y-auto pr-1">
        <div 
          v-for="item in cartStore.items" 
          :key="item.productId"
          class="flex items-center justify-between p-2.5 bg-gray-50 rounded-lg border border-gray-100"
        >
          <div class="flex-1 pr-2">
            <h4 class="text-xs font-semibold text-gray-800 truncate">{{ item.name }}</h4>
            <p class="text-xs text-blue-600 font-bold mt-0.5">{{ formatRupiah(item.price) }}</p>
          </div>

          <div class="flex items-center gap-2">
            <button 
              @click="cartStore.updateQty(item.productId, item.quantity - 1)"
              class="w-6 h-6 rounded bg-white border border-gray-300 flex items-center justify-center font-bold text-xs hover:bg-gray-100"
            >-</button>
            <span class="text-xs font-bold w-5 text-center">{{ item.quantity }}</span>
            <button 
              @click="cartStore.updateQty(item.productId, item.quantity + 1)"
              :disabled="item.quantity >= item.stock"
              class="w-6 h-6 rounded bg-white border border-gray-300 flex items-center justify-center font-bold text-xs hover:bg-gray-100 disabled:opacity-30"
            >+</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Summary & Checkout Button -->
    <div class="border-t border-gray-200 pt-4 mt-4">
      <div class="flex justify-between items-center mb-1 text-sm text-gray-600">
        <span>Total Item</span>
        <span class="font-semibold">{{ cartStore.totalQty }} pcs</span>
      </div>
      <div class="flex justify-between items-center mb-4 text-base font-bold text-gray-900">
        <span>Total Bayar</span>
        <span class="text-blue-600 text-lg">{{ formatRupiah(cartStore.totalAmount) }}</span>
      </div>
      <button 
        :disabled="cartStore.items.length === 0"
        class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white font-bold py-3 rounded-xl transition text-sm shadow-md"
      >
        Lanjut ke Pembayaran
      </button>
    </div>
  </div>
</template>