<script setup lang="ts">
import { Field, FieldDescription, FieldError, FieldLabel } from '@/components/ui/field'

/**
 * Label + input + pesan error (shadcn Field). Input di dalam slot sebaiknya diberi
 * `:aria-invalid="!!error || undefined"` supaya bordernya ikut merah.
 */
defineProps<{ label: string; for?: string; error?: string; required?: boolean; hint?: string }>()
</script>

<template>
  <Field :data-invalid="!!error || undefined" class="gap-2">
    <FieldLabel :for="$props.for">
      {{ label }} <span v-if="required" class="text-destructive">*</span>
    </FieldLabel>
    <slot />
    <FieldError v-if="error">{{ error }}</FieldError>
    <FieldDescription v-else-if="hint">{{ hint }}</FieldDescription>
  </Field>
</template>
