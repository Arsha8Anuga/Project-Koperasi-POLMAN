<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import ThemeToggle from '@/components/common/ThemeToggle.vue'
import UserMenu from '@/components/common/UserMenu.vue'
import { Separator } from '@/components/ui/separator'
import { SidebarTrigger } from '@/components/ui/sidebar'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const roleLabel: Record<string, string> = { OWNER: 'Owner', LOGISTIK: 'Logistik', ADMIN: 'Admin', KASIR: 'Kasir' }

async function logout() {
  await auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <header class="sticky top-0 z-30 flex h-16 shrink-0 items-center gap-2 border-b bg-background/85 px-4 backdrop-blur sm:px-6">
    <SidebarTrigger class="-ml-1" aria-label="Buka/tutup menu (Ctrl+B)" />
    <Separator orientation="vertical" class="mr-1 h-5!" />
    <p class="truncate text-[15px] font-semibold text-muted-foreground">{{ route.meta.title }}</p>

    <div class="ml-auto flex items-center gap-1.5">
      <ThemeToggle />
      <Separator orientation="vertical" class="mx-1 h-6!" />
      <UserMenu :name="auth.user?.name" :subtitle="roleLabel[auth.user?.role ?? '']" @logout="logout" />
    </div>
  </header>
</template>
