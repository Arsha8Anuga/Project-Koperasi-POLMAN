<script setup lang="ts">
import { computed, type Component } from 'vue'
import { useRoute } from 'vue-router'
import BrandMark from '@/components/common/BrandMark.vue'
import {
  Sidebar,
  SidebarContent,
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

const auth = useAuthStore()
const route = useRoute()

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
          <p class="truncate text-[15px] font-bold text-sidebar-accent-foreground">Toko Koperasi</p>
          <p class="text-xs text-sidebar-foreground/70">Panel Admin</p>
        </div>
      </RouterLink>
    </SidebarHeader>

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
    <SidebarRail />
  </Sidebar>
</template>
