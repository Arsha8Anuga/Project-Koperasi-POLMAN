<script setup lang="ts">
import { CircleCheckIcon, IdCardIcon, XIcon } from '@lucide/vue'
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Field, FieldError, FieldLabel } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { Spinner } from '@/components/ui/spinner'
import { errorMessage } from '@/services/api'
import { salesApi } from '@/services/salesApi'
import type { MemberLookup as Member } from '@/types'

const member = defineModel<Member | null>({ required: true })

const number = ref('')
const loading = ref(false)
const error = ref('')

async function check() {
  const value = number.value.trim()
  if (!value || loading.value) return
  loading.value = true
  error.value = ''
  try {
    member.value = await salesApi.lookupMember(value)
  } catch (e) {
    member.value = null
    error.value = errorMessage(e, 'Nomor anggota tidak ditemukan')
  } finally {
    loading.value = false
  }
}

function clear() {
  member.value = null
  number.value = ''
  error.value = ''
}
</script>

<template>
  <Field :data-invalid="!!error || undefined">
    <FieldLabel for="member-number">
      Anggota koperasi <span class="font-normal text-muted-foreground">(opsional)</span>
    </FieldLabel>

    <div v-if="member" class="flex items-center gap-3 rounded-md border border-success/30 bg-success-soft px-3 py-1.5">
      <CircleCheckIcon class="size-[18px] shrink-0 text-success" />
      <div class="min-w-0 flex-1 leading-tight">
        <p class="truncate text-sm font-semibold text-foreground">{{ member.name }}</p>
        <p class="font-mono text-xs text-muted-foreground">{{ member.memberNumber }}</p>
      </div>
      <Button variant="ghost" size="icon-sm" aria-label="Hapus anggota" @click="clear"><XIcon /></Button>
    </div>

    <form v-else class="flex gap-2" @submit.prevent="check">
      <div class="relative flex-1">
        <IdCardIcon class="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          id="member-number"
          v-model="number"
          class="bg-background pl-9 uppercase placeholder:normal-case"
          :aria-invalid="!!error || undefined"
          placeholder="contoh: KOP-001"
          autocomplete="off"
        />
      </div>
      <Button type="submit" variant="outline" :disabled="loading || !number.trim()">
        <Spinner v-if="loading" />
        Cek
      </Button>
    </form>
    <FieldError v-if="error">{{ error }}</FieldError>
  </Field>
</template>
