<script setup lang="ts">
defineProps<{ label: string; error?: string; required?: boolean }>()
</script>

<template>
  <div>
    <label class="mb-1 block text-sm font-medium">
      {{ label }} <span v-if="required" class="text-red-500">*</span>
    </label>
    <slot />
    <p v-if="error" class="mt-1 text-xs text-red-600">{{ error }}</p>
  </div>
</template>