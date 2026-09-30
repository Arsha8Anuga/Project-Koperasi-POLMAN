<script setup lang="ts">
import { HistoryIcon, ShoppingCartIcon } from '@lucide/vue'
import { useRouter } from 'vue-router'
import BrandMark from '@/components/common/BrandMark.vue'
import ThemeToggle from '@/components/common/ThemeToggle.vue'
import UserMenu from '@/components/common/UserMenu.vue'
import { Separator } from '@/components/ui/separator'
import { useAuthStore } from '@/stores/auth'
import { BRAND } from '@/utils/brand'

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
  <div class="flex h-dvh flex-col">
    <header class="z-20 flex h-16 shrink-0 items-center gap-2 px-3 sm:px-4">
      <!-- "breadcrumb" ala referensi: logo · nama koperasi / halaman -->
      <RouterLink
        :to="{ name: 'pos' }"
        class="flex items-center gap-2.5 rounded-xl bg-card p-1 shadow-xs ring-1 ring-border sm:pr-3.5"
      >
        <BrandMark size="sm" />
        <span class="hidden text-sm font-bold sm:inline">{{ BRAND.name }}</span>
      </RouterLink>
      <span class="text-muted-foreground/60 select-none" aria-hidden="true">/</span>

      <nav class="flex items-center gap-1" aria-label="Menu kasir">
        <RouterLink
          v-for="item in nav"
          :key="item.name"
          :to="{ name: item.name }"
          class="flex h-10 items-center gap-2 rounded-xl px-3 text-sm font-semibold text-muted-foreground transition outline-none hover:bg-card/70 hover:text-foreground focus-visible:ring-3 focus-visible:ring-ring/50"
          active-class="bg-card text-foreground! shadow-xs ring-1 ring-border"
        >
          <component :is="item.icon" class="size-4" />
          <span class="hidden sm:inline">{{ item.label }}</span>
        </RouterLink>
      </nav>

      <div class="ml-auto flex items-center gap-1 rounded-xl bg-card p-1 shadow-xs ring-1 ring-border">
        <ThemeToggle />
        <Separator orientation="vertical" class="mx-0.5 h-6!" />
        <UserMenu :name="auth.user?.name" subtitle="Kasir" @logout="logout" />
      </div>
    </header>

    <div class="min-h-0 flex-1">
      <RouterView />
    </div>
  </div>
</template>
