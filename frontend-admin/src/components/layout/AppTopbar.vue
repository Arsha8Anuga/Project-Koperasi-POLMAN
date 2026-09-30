<script setup lang="ts">
import { CalendarDaysIcon } from '@lucide/vue'
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ThemeToggle from '@/components/common/ThemeToggle.vue'
import UserMenu from '@/components/common/UserMenu.vue'
import { Separator } from '@/components/ui/separator'
import { SidebarTrigger } from '@/components/ui/sidebar'
import { appRoutes } from '@/router/routes'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const roleLabel: Record<string, string> = { OWNER: 'Owner', LOGISTIK: 'Logistik', ADMIN: 'Admin', KASIR: 'Kasir' }

/** Breadcrumb "Grup / Judul": grup diambil dari menu route (mis. Logistik / Produk Baru). */
const group = computed(() => {
  const own = route.meta.menu?.group
  if (own) return own
  // sub-halaman tanpa menu (detail/form): pakai grup menu induk dengan prefix path yang sama
  const parent = appRoutes.find((r) => r.meta?.menu && r.path && route.path.startsWith(`/${r.path.split('/')[0]}/`))
  return parent?.meta?.menu?.group ?? null
})

const today = new Intl.DateTimeFormat('id-ID', {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
  year: 'numeric',
  timeZone: 'Asia/Jakarta',
}).format(new Date())

async function logout() {
  await auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <header class="sticky top-0 z-30 flex h-16 shrink-0 items-center gap-2 border-b bg-background/85 px-4 backdrop-blur sm:px-6">
    <SidebarTrigger class="-ml-1" aria-label="Buka/tutup menu (Ctrl+B)" />
    <Separator orientation="vertical" class="mr-1 h-5!" />
    <nav class="flex min-w-0 items-center gap-1.5 text-[15px]" aria-label="Breadcrumb">
      <span v-if="group" class="hidden shrink-0 text-muted-foreground sm:inline">{{ group }}</span>
      <span v-if="group" class="hidden text-muted-foreground/50 sm:inline" aria-hidden="true">/</span>
      <span class="truncate font-semibold">{{ route.meta.title }}</span>
    </nav>

    <div class="ml-auto flex items-center gap-1.5">
      <span class="hidden items-center gap-1.5 rounded-lg border bg-card px-2.5 py-1.5 text-xs text-muted-foreground lg:flex">
        <CalendarDaysIcon class="size-3.5" /> {{ today }}
      </span>
      <ThemeToggle />
      <Separator orientation="vertical" class="mx-1 h-6!" />
      <UserMenu :name="auth.user?.name" :subtitle="roleLabel[auth.user?.role ?? '']" @logout="logout" />
    </div>
  </header>
</template>
