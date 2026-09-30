<script setup lang="ts">
import { LogOutIcon } from '@lucide/vue'
import { computed, type Component } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BrandMark from '@/components/common/BrandMark.vue'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from '@/components/ui/sidebar'
import { appRoutes } from '@/router/routes'
import { useAuthStore } from '@/stores/auth'
import { BRAND } from '@/utils/brand'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const roleLabel: Record<string, string> = { OWNER: 'Owner', LOGISTIK: 'Logistik', ADMIN: 'Admin', KASIR: 'Kasir' }
const initials = computed(() =>
  (auth.user?.name ?? '?')
    .split(' ')
    .map((w) => w[0])
    .join('')
    .slice(0, 2)
    .toUpperCase(),
)

async function logout() {
  await auth.logout()
  router.push({ name: 'login' })
}

/** Menu dibangun dari konfigurasi route yang sama dengan guard → menu & hak akses tidak mungkin beda. */
const groups = computed(() => {
  const map = new Map<string, { label: string; name: string; path: string; icon: Component }[]>()
  for (const r of appRoutes) {
    const menu = r.meta?.menu
    if (!menu || typeof r.name !== 'string') continue
    if (r.meta?.roles && !auth.hasRole(...r.meta.roles)) continue
    if (!map.has(menu.group)) map.set(menu.group, [])
    map.get(menu.group)!.push({ label: menu.label, name: r.name, path: `/${r.path}`, icon: menu.icon })
  }
  return [...map.entries()].map(([group, items]) => ({ group, items }))
})

/** Aktif juga untuk sub-halaman (mis. /logistik/products/123 → menu Produk). */
function isActive(path: string) {
  return route.path === path || (path !== '/' && route.path.startsWith(`${path}/`))
}
</script>

<template>
  <Sidebar collapsible="icon">
    <SidebarHeader class="h-16 justify-center border-b border-sidebar-border">
      <RouterLink :to="{ name: 'dashboard' }" class="flex items-center gap-3 px-1 group-data-[collapsible=icon]:px-0">
        <BrandMark size="sm" />
        <div class="min-w-0 leading-tight group-data-[collapsible=icon]:hidden">
          <p class="truncate text-[15px] font-bold text-sidebar-accent-foreground">{{ BRAND.name }}</p>
          <p class="text-xs text-sidebar-foreground/70">Panel Admin</p>
        </div>
      </RouterLink>
    </SidebarHeader>

    <!-- profil pengguna (referensi: sidebar dengan kartu profil di atas menu) -->
    <div class="border-b border-sidebar-border p-3 group-data-[collapsible=icon]:px-2">
      <div class="flex items-center gap-3 rounded-xl bg-sidebar-accent/60 p-2.5 group-data-[collapsible=icon]:justify-center group-data-[collapsible=icon]:bg-transparent group-data-[collapsible=icon]:p-0">
        <Avatar class="size-9 shrink-0 ring-2 ring-sidebar-primary/40 group-data-[collapsible=icon]:size-8">
          <AvatarFallback class="bg-sidebar-primary text-xs font-bold text-sidebar-primary-foreground">{{ initials }}</AvatarFallback>
        </Avatar>
        <div class="min-w-0 leading-tight group-data-[collapsible=icon]:hidden">
          <p class="truncate text-sm font-semibold text-sidebar-accent-foreground">{{ auth.user?.name }}</p>
          <p class="mt-0.5 flex items-center gap-1.5 text-xs text-sidebar-foreground/70">
            <span class="size-1.5 rounded-full bg-success" aria-hidden="true" />
            {{ roleLabel[auth.user?.role ?? ''] ?? auth.user?.role }}
          </p>
        </div>
      </div>
    </div>

    <SidebarContent class="py-2">
      <SidebarGroup v-for="g in groups" :key="g.group">
        <SidebarGroupLabel class="text-[11px] font-bold tracking-wider text-sidebar-foreground/60 uppercase">
          {{ g.group }}
        </SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="item in g.items" :key="item.name">
              <SidebarMenuButton as-child :is-active="isActive(item.path)" :tooltip="item.label" class="h-9 font-medium">
                <RouterLink :to="{ name: item.name }">
                  <component :is="item.icon" />
                  <span>{{ item.label }}</span>
                </RouterLink>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>
    <SidebarFooter class="border-t border-sidebar-border">
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton tooltip="Keluar" class="h-9 font-medium text-sidebar-foreground/80 hover:text-destructive" @click="logout">
            <LogOutIcon />
            <span>Keluar</span>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarFooter>
    <SidebarRail />
  </Sidebar>
</template>
