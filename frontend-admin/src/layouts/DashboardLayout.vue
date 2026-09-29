<script setup lang="ts">
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppTopbar from '@/components/layout/AppTopbar.vue'
import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar'
</script>

<!-- Sidebar shadcn: bisa diciutkan jadi ikon (Ctrl+B), jadi drawer di layar kecil. -->
<template>
  <SidebarProvider>
    <AppSidebar />
    <SidebarInset class="min-w-0">
      <AppTopbar />
      <div class="mx-auto w-full max-w-7xl flex-1 px-4 py-6 sm:px-6 lg:px-8">
        <RouterView />
      </div>
    </SidebarInset>
  </SidebarProvider>
</template>
