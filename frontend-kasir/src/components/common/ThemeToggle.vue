<script setup lang="ts">
import { MoonIcon, SunIcon } from '@lucide/vue'
import { Button } from '@/components/ui/button'
import { useTheme } from '@/composables/useTheme'

const { theme, toggle } = useTheme()
</script>

<template>
  <Button
    variant="ghost"
    size="icon"
    :title="theme === 'dark' ? 'Ganti ke mode terang' : 'Ganti ke mode gelap'"
    :aria-label="theme === 'dark' ? 'Ganti ke mode terang' : 'Ganti ke mode gelap'"
    @click="toggle"
  >
    <SunIcon v-if="theme === 'dark'" class="size-[18px]" />
    <MoonIcon v-else class="size-[18px]" />
  </Button>
</template>
