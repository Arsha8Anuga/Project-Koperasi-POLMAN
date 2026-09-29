<script setup lang="ts">
import { Toaster } from '@/components/ui/sonner'
import { useTheme } from '@/composables/useTheme'

const { theme } = useTheme()
</script>

<template>
  <RouterView />
  <Toaster :theme="theme" position="bottom-right" rich-colors close-button />
</template>
