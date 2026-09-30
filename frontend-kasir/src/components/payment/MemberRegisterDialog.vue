<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Field, FieldDescription, FieldError, FieldLabel } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { Spinner } from '@/components/ui/spinner'
import { ApiException, errorMessage } from '@/services/api'
import { memberApi } from '@/services/memberApi'
import type { Member } from '@/types'

/**
 * Pendaftaran anggota oleh kasir. Kasir hanya bisa MENDAFTARKAN;
 * mengubah data dan menonaktifkan anggota dilakukan admin.
 */
const open = defineModel<boolean>('open', { required: true })
const emit = defineEmits<{ registered: [Member] }>()

const form = reactive({ name: '', phone: '' })
const errors = reactive<{ name?: string; phone?: string }>({})
const saving = ref(false)
const error = ref('')

watch(open, (v) => {
  if (!v) return
  form.name = ''
  form.phone = ''
  errors.name = errors.phone = undefined
  error.value = ''
})

function validate() {
  errors.name = form.name.trim() ? undefined : 'Nama wajib diisi'
  const phone = form.phone.trim()
  errors.phone = phone && !/^\+?[0-9]{8,15}$/.test(phone) ? 'Telepon 8–15 digit angka' : undefined
  return !errors.name && !errors.phone
}

async function submit() {
  if (saving.value || !validate()) return
  saving.value = true
  error.value = ''
  try {
    const m = await memberApi.register({ name: form.name.trim(), phone: form.phone.trim() || null })
    emit('registered', m)
    open.value = false
  } catch (e) {
    if (e instanceof ApiException && e.code === 'VALIDATION_ERROR') {
      for (const d of e.details as { field?: string; message?: string }[]) {
        if (d.field === 'name' || d.field === 'phone') errors[d.field] = d.message
      }
    }
    error.value = errorMessage(e, 'Gagal mendaftarkan anggota')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <Dialog v-model:open="open">
    <DialogContent class="sm:max-w-md">
      <DialogHeader>
        <DialogTitle>Daftarkan anggota baru</DialogTitle>
        <DialogDescription>Nomor anggota dibuat otomatis dan langsung dipakai untuk transaksi ini.</DialogDescription>
      </DialogHeader>

      <form class="space-y-4" novalidate @submit.prevent="submit">
        <Alert v-if="error" variant="destructive">
          <AlertDescription>{{ error }}</AlertDescription>
        </Alert>
        <Field :data-invalid="!!errors.name || undefined">
          <FieldLabel for="new-member-name">Nama lengkap <span class="text-destructive">*</span></FieldLabel>
          <Input id="new-member-name" v-model="form.name" maxlength="60" autocomplete="off" autofocus :aria-invalid="!!errors.name || undefined" />
          <FieldError v-if="errors.name">{{ errors.name }}</FieldError>
        </Field>
        <Field :data-invalid="!!errors.phone || undefined">
          <FieldLabel for="new-member-phone">Telepon</FieldLabel>
          <Input
            id="new-member-phone"
            v-model="form.phone"
            inputmode="tel"
            placeholder="0812…"
            autocomplete="off"
            :aria-invalid="!!errors.phone || undefined"
          />
          <FieldError v-if="errors.phone">{{ errors.phone }}</FieldError>
          <FieldDescription v-else>Opsional</FieldDescription>
        </Field>
        <DialogFooter>
          <Button type="button" variant="outline" @click="open = false">Batal</Button>
          <Button type="submit" :disabled="saving"><Spinner v-if="saving" /> Daftarkan</Button>
        </DialogFooter>
      </form>
    </DialogContent>
  </Dialog>
</template>
