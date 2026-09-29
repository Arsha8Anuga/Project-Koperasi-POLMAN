<script setup lang="ts">
defineProps<{ label: string; value: string; accent?: 'blue' | 'green' | 'yellow' | 'red' }>()
</script>

<template>
  <div class="rounded-xl border bg-white p-5">
    <p class="text-sm text-gray-500">{{ label }}</p>
    <p
      class="mt-1 text-2xl font-bold"
      :class="{
        'text-blue-700': accent === 'blue' || !accent,
        'text-green-700': accent === 'green',
        'text-yellow-700': accent === 'yellow',
        'text-red-700': accent === 'red',
      }"
    >
      {{ value }}
    </p>
  </div>
</template>