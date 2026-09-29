<script setup lang="ts">
import { ref } from 'vue'
import type { MemberLookupResult } from '../../types/member'

defineProps<{
  member: MemberLookupResult | null
  loading?: boolean
  error?: string
}>()

const emit = defineEmits<{
  (e: 'check', memberNumber: string): void
  (e: 'clear'): void
}>()

const memberNumber = ref('')

function check() {
  if (!memberNumber.value.trim()) return
  emit('check', memberNumber.value.trim())
}

function clear() {
  memberNumber.value = ''
  emit('clear')
}
</script>

<template>
  <div class="max-w-sm mx-auto rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
    <label class="block text-xs font-semibold uppercase tracking-wide text-slate-400">
      Nomor anggota (opsional)
      <input
        v-model="memberNumber"
        placeholder="contoh: KOP-001"
        :disabled="!!member"
        class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm text-slate-800 outline-none transition focus:border-indigo-400 focus:bg-white focus:ring-4 focus:ring-indigo-100 disabled:bg-slate-100 disabled:text-slate-400"
      />
    </label>

    <button
      v-if="!member"
      type="button"
      :disabled="loading || !memberNumber.trim()"
      @click="check"
      class="mt-3 w-full rounded-xl bg-indigo-50 py-2 text-sm font-semibold text-indigo-600 transition hover:bg-indigo-100 disabled:bg-slate-100 disabled:text-slate-400"
    >
      {{ loading ? 'Mengecek...' : 'Cek' }}
    </button>
    <button
      v-else
      type="button"
      @click="clear"
      class="mt-3 w-full rounded-xl bg-slate-100 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-200"
    >
      Hapus
    </button>

    <p v-if="member" class="mt-2 text-xs font-medium text-emerald-600">
      Anggota: {{ member.name }} ({{ member.memberNumber }})
    </p>
    <p v-else-if="error" class="mt-2 text-xs font-medium text-rose-500">{{ error }}</p>
  </div>
</template>