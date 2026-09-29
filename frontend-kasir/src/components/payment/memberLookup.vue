<script setup lang="ts">
import { ref } from 'vue'
import type { MemberLookupResult } from '../../types/member'

defineProps<{
  member: MemberLookupResult | null // anggota yang sudah ditemukan (dari induk)
  loading?: boolean
  error?: string // pesan error dari induk
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
  <div class="box">
    <label>
      Nomor anggota (opsional)
      <input v-model="memberNumber" placeholder="contoh: KOP-001" :disabled="!!member" />
    </label>

    <button v-if="!member" type="button" :disabled="loading || !memberNumber.trim()" @click="check">
      {{ loading ? 'Mengecek...' : 'Cek' }}
    </button>
    <button v-else type="button" @click="clear">Hapus</button>

    <p v-if="member" class="ok">Anggota: {{ member.name }} ({{ member.memberNumber }})</p>
    <p v-else-if="error" class="warn">{{ error }}</p>
  </div>
</template>

<style scoped>
.box { max-width: 320px; margin: 16px auto; padding: 16px; border: 1px solid #ccc; }
input { display: block; width: 100%; padding: 6px; margin: 4px 0 8px; }
.ok { color: #060; }
.warn { color: #c00; }
</style>