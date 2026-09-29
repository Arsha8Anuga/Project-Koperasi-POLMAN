<script setup lang="ts">
import { LogOut } from 'lucide-vue-next'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

function logout() {
  auth.logout()
  router.push('/login')
}

const roleStyle: Record<string, string> = {
  OWNER: 'bg-purple-100 text-purple-700',
  LOGISTIK: 'bg-blue-100 text-blue-700',
  ADMIN: 'bg-blue-100 text-blue-700',
  KASIR: 'bg-green-100 text-green-700',
}
</script>

<template>
  <header class="flex h-14 items-center justify-between border-b bg-white px-6">
    <h1 class="font-semibold">{{ route.meta.title }}</h1>
    <div class="flex items-center gap-3">
      <span
        class="rounded-full px-2.5 py-1 text-xs font-semibold"
        :class="roleStyle[auth.user?.role ?? ''] ?? 'bg-gray-100 text-gray-600'"
      >
        {{ auth.user?.role }}
      </span>
      <button
        class="flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm text-gray-600 transition hover:border-red-200 hover:bg-red-50 hover:text-red-600"
        @click="logout"
      >
        <LogOut :size="15" />
        Logout
      </button>
    </div>
  </header>
</template>