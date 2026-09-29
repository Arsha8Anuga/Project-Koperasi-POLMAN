<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';

import ProductCard from '../components/product/ProductCard.vue';
import CartPanel from '../components/cart/CartPanel.vue';
import type { Product } from '../types';

import { useAuthStore } from '../stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
};

const products = ref<Product[]>([
  {
    id: '1',
    sku: 'PRD-001',
    barcode: '8991001',
    name: 'Kopi Susu Gula Aren',
    categoryId: 'c1',
    categoryName: 'Minuman',
    unit: 'Cup',
    sellingPrice: 18000,
    stock: 15,
    minimumStock: 5,
    stockStatus: 'OK',
    imageUrl:
      'https://images.unsplash.com/photo-1541167760496-1628856ab772?w=600&auto=format&fit=crop&q=85',
    isActive: true
  },
  {
    id: '2',
    sku: 'PRD-002',
    barcode: '8991002',
    name: 'Roti Bakar Cokelat Keju',
    categoryId: 'c2',
    categoryName: 'Makanan',
    unit: 'Porsi',
    sellingPrice: 22000,
    stock: 3,
    minimumStock: 5,
    stockStatus: 'LOW',
    imageUrl:
      'https://images.unsplash.com/photo-1484723091739-30a097e8f929?w=600&auto=format&fit=crop&q=85',
    isActive: true
  },
  {
    id: '3',
    sku: 'PRD-003',
    barcode: '8991003',
    name: 'Air Mineral 600ml',
    categoryId: 'c1',
    categoryName: 'Minuman',
    unit: 'Botol',
    sellingPrice: 5000,
    stock: 0,
    minimumStock: 10,
    stockStatus: 'OUT',
    imageUrl:
      'https://images.unsplash.com/photo-1523362628745-0c100150b504?w=600&auto=format&fit=crop&q=85',
    isActive: true
  },
  {
    id: '4',
    sku: 'PRD-004',
    barcode: '8991004',
    name: 'Kentang Goreng Original',
    categoryId: 'c2',
    categoryName: 'Makanan',
    unit: 'Porsi',
    sellingPrice: 15000,
    stock: 20,
    minimumStock: 5,
    stockStatus: 'OK',
    imageUrl:
      'https://images.unsplash.com/photo-1576107232684-1279f390859f?w=600&auto=format&fit=crop&q=85',
    isActive: true
  }
]);

const searchQuery = ref('');
const selectedCategory = ref('ALL');

const categories = [
  {
    id: 'ALL',
    name: 'Semua Produk'
  },
  {
    id: 'c1',
    name: '☕ Minuman'
  },
  {
    id: 'c2',
    name: '🍔 Makanan'
  }
];

const filteredProducts = computed(() => {
  return products.value.filter((p) => {
    const query = searchQuery.value.toLowerCase();

    const matchSearch =
      p.name.toLowerCase().includes(query) ||
      p.sku.toLowerCase().includes(query);

    const matchCategory =
      selectedCategory.value === 'ALL' ||
      p.categoryId === selectedCategory.value;

    return matchSearch && matchCategory;
  });
});

const totalProducts = computed(() => {
  return products.value.length;
});

const availableProducts = computed(() => {
  return products.value.filter((p) => p.stock > 0).length;
});

const lowStockProducts = computed(() => {
  return products.value.filter(
    (p) => p.stock > 0 && p.stock <= p.minimumStock
  ).length;
});
</script>

<template>
  <div class="flex h-screen bg-slate-100 text-slate-800 font-sans">

    <!-- ================= MAIN CONTENT ================= -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">

      <!-- ================= HEADER ================= -->
      <header class="bg-white border-b border-slate-200">

        <div class="px-6 py-4 flex items-center justify-between gap-6">

          <!-- BRAND -->
          <div class="flex items-center gap-3 shrink-0">

            <div
              class="w-11 h-11 rounded-2xl bg-indigo-600 flex items-center justify-center text-white text-xl font-black shadow-lg shadow-indigo-200"
            >
              K
            </div>

            <div>
              <h1 class="text-lg font-bold text-slate-900">
                Kasir POS
              </h1>

              <p class="text-xs text-slate-400">
                Sistem Penjualan Toko
              </p>
            </div>

          </div>


          <!-- SEARCH -->
          <div class="flex-1 max-w-2xl">

            <div class="relative">

              <div
                class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none"
              >
                <span class="text-slate-400 text-lg">
                  🔍
                </span>
              </div>

              <input
                v-model="searchQuery"
                type="text"
                placeholder="Cari produk atau SKU..."
                class="w-full pl-11 pr-10 py-3 rounded-2xl bg-slate-50 border border-slate-200 text-sm text-slate-700 placeholder-slate-400 outline-none transition-all focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-100"
              />

              <!-- CLEAR SEARCH -->
              <div
                v-if="searchQuery"
                class="absolute inset-y-0 right-0 pr-4 flex items-center"
              >
                <button
                  @click="searchQuery = ''"
                  class="text-slate-400 hover:text-slate-700 transition"
                >
                  ✕
                </button>
              </div>

            </div>

          </div>


          <!-- USER / STATUS / LOGOUT -->
          <div
            class="hidden lg:flex items-center gap-3 shrink-0"
          >

            <div class="text-right">

              <p class="text-xs font-semibold text-slate-700">
                Kasir
              </p>

              <p class="text-[11px] text-slate-400">
                Online
              </p>

            </div>

            <!-- USER AVATAR -->
            <div
              class="w-10 h-10 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold"
            >
              K
            </div>

            <!-- LOGOUT -->
            <button
              @click="handleLogout"
              class="px-3 py-1.5 bg-rose-50 hover:bg-rose-100 text-rose-600 text-xs font-semibold rounded-lg border border-rose-200 transition"
            >
              Keluar / Logout
            </button>

          </div>

        </div>


        <!-- ================= MINI STATISTICS ================= -->
        <div class="px-6 pb-4">

          <div class="grid grid-cols-3 gap-3 max-w-2xl">

            <!-- TOTAL PRODUK -->
            <div
              class="bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5"
            >

              <p
                class="text-[10px] uppercase tracking-wide text-slate-400 font-semibold"
              >
                Produk
              </p>

              <p class="text-lg font-bold text-slate-800">
                {{ totalProducts }}
              </p>

            </div>


            <!-- PRODUK TERSEDIA -->
            <div
              class="bg-emerald-50 border border-emerald-100 rounded-xl px-4 py-2.5"
            >

              <p
                class="text-[10px] uppercase tracking-wide text-emerald-500 font-semibold"
              >
                Tersedia
              </p>

              <p class="text-lg font-bold text-emerald-700">
                {{ availableProducts }}
              </p>

            </div>


            <!-- STOK MENIPIS -->
            <div
              class="bg-amber-50 border border-amber-100 rounded-xl px-4 py-2.5"
            >

              <p
                class="text-[10px] uppercase tracking-wide text-amber-500 font-semibold"
              >
                Stok Menipis
              </p>

              <p class="text-lg font-bold text-amber-700">
                {{ lowStockProducts }}
              </p>

            </div>

          </div>

        </div>

      </header>


      <!-- ================= CATEGORY ================= -->
      <div
        class="bg-white border-b border-slate-200 px-6 py-3"
      >

        <div
          class="flex items-center gap-2 overflow-x-auto"
        >

          <span
            class="text-xs font-semibold text-slate-400 mr-2 shrink-0"
          >
            KATEGORI
          </span>


          <button
            v-for="cat in categories"
            :key="cat.id"
            @click="selectedCategory = cat.id"
            :class="[
              'px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all duration-200',
              selectedCategory === cat.id
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-200'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            ]"
          >
            {{ cat.name }}
          </button>

        </div>

      </div>


      <!-- ================= PRODUCT AREA ================= -->
      <main class="flex-1 overflow-y-auto p-6">

        <!-- RESULT HEADER -->
        <div
          class="flex items-center justify-between mb-5"
        >

          <div>

            <h2 class="text-base font-bold text-slate-900">
              Daftar Produk
            </h2>

            <p class="text-xs text-slate-400 mt-0.5">
              {{ filteredProducts.length }} produk ditemukan
            </p>

          </div>

        </div>


        <!-- PRODUCT GRID -->
        <div
          v-if="filteredProducts.length > 0"
          class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-5"
        >

          <ProductCard
            v-for="product in filteredProducts"
            :key="product.id"
            :product="product"
          />

        </div>


        <!-- EMPTY STATE -->
        <div
          v-else
          class="h-64 flex flex-col items-center justify-center text-center"
        >

          <div
            class="w-16 h-16 rounded-full bg-slate-200 flex items-center justify-center text-2xl mb-4"
          >
            🔍
          </div>

          <h3 class="font-bold text-slate-700">
            Produk tidak ditemukan
          </h3>

          <p class="text-sm text-slate-400 mt-1">
            Coba gunakan kata kunci atau kategori lain.
          </p>

          <button
            @click="searchQuery = ''; selectedCategory = 'ALL'"
            class="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-semibold hover:bg-indigo-700 transition"
          >
            Reset Filter
          </button>

        </div>

      </main>

    </div>


    <!-- ================= CART ================= -->
    <aside
      class="w-80 xl:w-96 border-l border-slate-200 bg-white shadow-[-4px_0_20px_rgba(0,0,0,0.04)] flex flex-col"
    >

      <CartPanel />

    </aside>

  </div>
</template>