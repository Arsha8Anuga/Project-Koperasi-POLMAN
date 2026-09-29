<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function submit() {
  if (!username.value || !password.value) {
    error.value = 'Username dan password wajib diisi'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await auth.login(username.value, password.value)
    router.push((route.query.redirect as string) || '/')
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Login gagal'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-gray-50 p-4">
    <form class="w-full max-w-sm space-y-4 rounded-xl bg-white p-8 shadow" @submit.prevent="submit">
      <h1 class="text-xl font-bold">Admin Koperasi</h1>
      <p class="text-sm text-gray-500">Masuk untuk melanjutkan</p>

      <div>
        <label class="mb-1 block text-sm font-medium" for="username">Username</label>
        <input id="username" v-model="username" type="text" autocomplete="username"
          class="w-full rounded-lg border px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium" for="password">Password</label>
        <input id="password" v-model="password" type="password" autocomplete="current-password"
          class="w-full rounded-lg border px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500" />
      </div>

      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

      <button type="submit" :disabled="loading"
        class="w-full rounded-lg bg-blue-600 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50">
        {{ loading ? 'Memproses...' : 'Masuk' }}
      </button>
    </form>
  </div>
</template>