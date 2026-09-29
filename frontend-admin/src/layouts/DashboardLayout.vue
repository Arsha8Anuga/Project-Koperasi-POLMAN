<script setup lang="ts">
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppTopbar from '@/components/layout/AppTopbar.vue'
</script>

<template>
  <div class="flex min-h-screen bg-gray-50">
    <AppSidebar />
    <div class="flex min-w-0 flex-1 flex-col">
      <AppTopbar />
      <main class="flex-1 p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>