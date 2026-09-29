<script setup lang="ts">
import type { Product } from '../../types';
import { useCartStore } from '../../stores/cart';

const props = defineProps<{ product: Product }>();
const cartStore = useCartStore();

const formatRupiah = (val: number) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    maximumFractionDigits: 0
  }).format(val);
};
</script>

<template>
  <div
    @click="product.stock > 0 && cartStore.addItem(product)"
    :class="[
      'group relative bg-white rounded-2xl border overflow-hidden flex flex-col transition-all duration-300 select-none',
      product.stock === 0
        ? 'border-slate-200 opacity-60 cursor-not-allowed'
        : 'border-slate-200 cursor-pointer hover:border-indigo-300 hover:shadow-xl hover:shadow-slate-200/70 hover:-translate-y-1'
    ]"
  >
    <!-- IMAGE -->
    <div class="relative h-40 bg-slate-100 overflow-hidden">
      <img
        v-if="product.imageUrl"
        :src="product.imageUrl"
        :alt="product.name"
        class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
      />
      <div v-else class="w-full h-full flex items-center justify-center text-slate-400 text-xs">
        Tanpa Gambar
      </div>

      <!-- IMAGE OVERLAY -->
      <div class="absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-transparent opacity-60"></div>

      <!-- STOCK BADGE -->
      <div class="absolute top-3 right-3">
        <span
          :class="[
            'inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-full text-[10px] font-bold backdrop-blur-md shadow-sm',
            product.stockStatus === 'OK'
              ? 'bg-emerald-500/90 text-white'
              : product.stockStatus === 'LOW'
                ? 'bg-amber-500/90 text-white'
                : 'bg-rose-500/90 text-white'
          ]"
        >
          <span class="w-1.5 h-1.5 rounded-full bg-white"></span>
          {{
            product.stock === 0
              ? 'Habis'
              : product.stock <= product.minimumStock
                ? `Sisa ${product.stock}`
                : `Stok ${product.stock}`
          }}
        </span>
      </div>

      <!-- OUT OF STOCK -->
      <div v-if="product.stock === 0" class="absolute inset-0 flex items-center justify-center">
        <span class="bg-slate-900/80 text-white px-4 py-2 rounded-xl text-xs font-bold backdrop-blur-sm">
          PRODUK HABIS
        </span>
      </div>
    </div>

    <!-- PRODUCT INFO -->
    <div class="p-4 flex flex-col flex-1">
      <!-- SKU + CATEGORY -->
      <div class="flex items-center justify-between gap-2 mb-2">
        <span class="text-[10px] font-mono text-slate-400 tracking-wide">
          {{ product.sku }}
        </span>
        <span class="text-[10px] font-medium px-2 py-1 rounded-lg bg-indigo-50 text-indigo-600 truncate max-w-[90px]">
          {{ product.categoryName }}
        </span>
      </div>

      <!-- NAME -->
      <h3 class="font-bold text-sm text-slate-800 line-clamp-2 min-h-[40px] leading-5 group-hover:text-indigo-600 transition-colors">
        {{ product.name }}
      </h3>

      <!-- UNIT -->
      <p class="text-[11px] text-slate-400 mt-1">
        Satuan: {{ product.unit }}
      </p>

      <!-- PRICE + BUTTON -->
      <div class="mt-auto pt-4 flex items-end justify-between gap-2">
        <div>
          <p class="text-[10px] text-slate-400 mb-0.5">Harga</p>
          <span class="text-base font-black text-indigo-600">
            {{ formatRupiah(product.sellingPrice) }}
          </span>
        </div>

        <button
          :disabled="product.stock === 0"
          @click.stop="product.stock > 0 && cartStore.addItem(product)"
          :class="[
            'flex items-center gap-1.5 px-3 py-2.5 rounded-xl text-xs font-bold transition-all',
            product.stock > 0
              ? 'bg-indigo-600 hover:bg-indigo-700 active:scale-95 text-white shadow-md shadow-indigo-200'
              : 'bg-slate-200 text-slate-400 cursor-not-allowed'
          ]"
        >
          <span class="text-base leading-none">+</span>
          Tambah
        </button>
      </div>
    </div>
  </div>
</template>