<script setup lang="ts">
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { appRoutes } from '@/router/routes'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const collapsed = ref(false)

const groups = computed(() => {
  const map = new Map<string, { label: string; path: string }[]>()
  for (const r of appRoutes) {
    const menu = r.meta?.menu
    if (!menu) continue
    if (r.meta?.roles && !auth.hasRole(...r.meta.roles)) continue
    if (!map.has(menu.group)) map.set(menu.group, [])
    const path = r.path === '' ? '/' : r.path
    map.get(menu.group)!.push({ label: menu.label, path })
  }
  return [...map.entries()].map(([group, items]) => ({ group, items }))
})
</script>

<template>
  <aside
    class="relative flex shrink-0 flex-col border-r bg-white transition-all duration-200"
    :class="collapsed ? 'w-16' : 'w-60'"
  >
    <div class="flex h-14 items-center border-b px-5">
      <span v-if="!collapsed" class="truncate text-lg font-bold text-blue-700">Koperasi Admin</span>
      <span v-else class="text-lg font-bold text-blue-700">K</span>
    </div>

    <nav class="flex-1 space-y-5 overflow-y-auto p-3">
      <div v-for="g in groups" :key="g.group">
        <p v-if="!collapsed" class="px-3 pb-1 text-xs font-semibold uppercase tracking-wide text-gray-400">
          {{ g.group }}
        </p>
        <RouterLink
          v-for="item in g.items"
          :key="item.path"
          :to="item.path"
          class="block truncate rounded-lg px-3 py-2 text-sm text-gray-700 hover:bg-gray-100"
          :class="collapsed ? 'text-center' : ''"
          active-class="!bg-blue-50 !font-semibold !text-blue-700"
          :title="item.label"
        >
          {{ collapsed ? item.label.charAt(0) : item.label }}
        </RouterLink>
      </div>
    </nav>

    <button
      class="absolute -right-3 top-16 flex h-6 w-6 items-center justify-center rounded-full border bg-white text-gray-500 shadow-sm hover:bg-gray-50"
      @click="collapsed = !collapsed"
    >
      <ChevronLeft v-if="!collapsed" :size="14" />
      <ChevronRight v-else :size="14" />
    </button>
  </aside>
</template>