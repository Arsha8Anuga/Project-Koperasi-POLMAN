<script setup lang="ts">
import { HistoryIcon, ShoppingCartIcon } from '@lucide/vue'
import { useRouter } from 'vue-router'
import BrandMark from '@/components/common/BrandMark.vue'
import ThemeToggle from '@/components/common/ThemeToggle.vue'
import UserMenu from '@/components/common/UserMenu.vue'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const nav = [
  { name: 'pos', label: 'Kasir', icon: ShoppingCartIcon },
  { name: 'history', label: 'Riwayat', icon: HistoryIcon },
]

async function logout() {
  await auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="flex h-screen flex-col">
    <header class="z-20 flex h-16 shrink-0 items-center gap-4 border-b bg-card px-4 sm:px-6">
      <RouterLink :to="{ name: 'pos' }" class="flex items-center gap-3">
        <BrandMark />
        <div class="hidden leading-tight sm:block">
          <p class="text-[15px] font-bold">Toko Koperasi</p>
          <p class="text-xs text-muted-foreground">Aplikasi Kasir</p>
        </div>
      </RouterLink>

      <nav class="ml-2 flex items-center gap-1 sm:ml-6">
        <Button v-for="item in nav" :key="item.name" as-child variant="ghost" class="font-semibold text-muted-foreground">
          <RouterLink :to="{ name: item.name }" active-class="bg-accent text-accent-foreground">
            <component :is="item.icon" />
            <span class="hidden sm:inline">{{ item.label }}</span>
          </RouterLink>
        </Button>
      </nav>

      <div class="ml-auto flex items-center gap-1.5">
        <ThemeToggle />
        <Separator orientation="vertical" class="mx-1 h-6!" />
        <UserMenu :name="auth.user?.name" subtitle="Kasir" @logout="logout" />
      </div>
    </header>

    <div class="min-h-0 flex-1">
      <RouterView />
    </div>
  </div>
</template>
