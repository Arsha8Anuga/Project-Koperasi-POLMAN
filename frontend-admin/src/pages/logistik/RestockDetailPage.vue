<script setup lang="ts">
import { ArrowLeftIcon } from '@lucide/vue'
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import TransactionBody from '@/pages/owner/TransactionBody.vue'
import { restockApi } from '@/services/api'
import { errorMessage } from '@/services/apiClient'
import { useAuthStore } from '@/stores/auth'
import type { Transaction } from '@/types/api'
import { formatDateTime } from '@/utils/format'

const route = useRoute()
const auth = useAuthStore()
const trx = ref<Transaction | null>(null)
const error = ref('')

onMounted(async () => {
  try {
    trx.value = await restockApi.get(String(route.params.id))
  } catch (e) {
    error.value = errorMessage(e, 'Restock tidak ditemukan')
  }
})
</script>

<template>
  <Button as-child variant="ghost" size="sm" class="mb-4 -ml-2">
    <RouterLink :to="auth.hasRole('LOGISTIK') ? { name: 'restocks' } : { name: 'owner-transactions' }">
      <ArrowLeftIcon /> Kembali
    </RouterLink>
  </Button>

  <ErrorAlert v-if="error" :message="error" />
  <div v-else-if="!trx" class="space-y-4">
    <Skeleton class="h-16 w-72" />
    <Skeleton class="h-72 w-full rounded-xl" />
  </div>
  <template v-else>
    <div class="mb-6">
      <Badge variant="soft" class="mb-2">Restock</Badge>
      <h1 class="font-mono text-2xl font-bold tracking-tight">{{ trx.code }}</h1>
      <p class="mt-1 text-sm text-muted-foreground">{{ formatDateTime(trx.createdAt) }} · dicatat oleh {{ trx.createdBy.name }}</p>
    </div>
    <TransactionBody :trx="trx" />
  </template>
</template>
