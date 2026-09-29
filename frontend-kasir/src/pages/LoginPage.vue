<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const username = ref('');
const password = ref('');
const isLoading = ref(false);
const errorMessage = ref('');

const handleLogin = async () => {
  if (!username.value || !password.value) {
    errorMessage.value = 'Username dan password wajib diisi';
    return;
  }

  isLoading.value = true;
  errorMessage.value = '';

  const result = await authStore.login({
    username: username.value,
    password: password.value,
  });

  isLoading.value = false;

  if (result.success) {
    router.push('/pos');
  } else {
    errorMessage.value = result.message || 'Login gagal';
  }
};
</script>

<template>
  <div class="min-h-screen bg-slate-100 flex items-center justify-center p-4">
    <div class="w-full max-w-md bg-white rounded-3xl shadow-xl border border-slate-200 p-8">
      <!-- HEADER LOGO -->
      <div class="text-center mb-8">
        <div class="w-16 h-16 bg-indigo-600 rounded-2xl flex items-center justify-center text-white text-3xl font-black mx-auto mb-3 shadow-lg shadow-indigo-200">
          K
        </div>
        <h1 class="text-2xl font-bold text-slate-900">Kasir POS</h1>
        <p class="text-xs text-slate-400 mt-1">Masuk dengan akun Kasir Anda</p>
      </div>

      <!-- ERROR ALERT -->
      <div v-if="errorMessage" class="mb-4 p-3 bg-rose-50 border border-rose-200 text-rose-600 text-xs font-semibold rounded-xl text-center">
        {{ errorMessage }}
      </div>

      <!-- FORM -->
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-xs font-semibold text-slate-600 mb-1.5">Username</label>
          <input
            v-model="username"
            type="text"
            placeholder="Masukkan username kasir..."
            class="w-full px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 text-sm outline-none focus:bg-white focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 transition"
          />
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-600 mb-1.5">Password</label>
          <input
            v-model="password"
            type="password"
            placeholder="••••••••"
            class="w-full px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 text-sm outline-none focus:bg-white focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 transition"
          />
        </div>

        <button
          type="submit"
          :disabled="isLoading"
          class="w-full py-3.5 bg-indigo-600 hover:bg-indigo-700 active:scale-[0.99] text-white text-sm font-bold rounded-xl shadow-lg shadow-indigo-200 transition duration-200 flex items-center justify-center gap-2"
        >
          <span v-if="isLoading" class="animate-spin text-lg">⏳</span>
          <span>{{ isLoading ? 'Memproses...' : 'Masuk ke Sistem POS' }}</span>
        </button>
      </form>
    </div>
  </div>
</template>