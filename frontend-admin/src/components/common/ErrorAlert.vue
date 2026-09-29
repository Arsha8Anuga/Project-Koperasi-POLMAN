<script setup lang="ts">
import { CircleAlertIcon } from '@lucide/vue'
import { Alert, AlertDescription } from '@/components/ui/alert'

defineProps<{ message: string }>()
</script>

<template>
  <Alert variant="destructive">
    <CircleAlertIcon />
    <AlertDescription>{{ message }}</AlertDescription>
  </Alert>
</template>
