<script setup lang="ts">
import { ArrowLeftIcon } from '@lucide/vue'
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { transactionApi } from '@/services/api'
import { errorMessage } from '@/services/apiClient'
import type { Transaction } from '@/types/api'
import { formatDateTime, formatRupiah } from '@/utils/format'
import TransactionBody from './TransactionBody.vue'

const route = useRoute()
const trx = ref<Transaction | null>(null)
const error = ref('')

onMounted(async () => {
  try {
    trx.value = await transactionApi.get(String(route.params.id))
  } catch (e) {
    error.value = errorMessage(e, 'Transaksi tidak ditemukan')
  }
})

const grossProfit = computed(() =>
  trx.value?.type === 'SALE'
    ? trx.value.items.reduce((n, i) => n + i.subtotal - i.quantity * (i.costPrice ?? 0), 0)
    : null,
)
</script>

<template>
  <Button as-child variant="ghost" size="sm" class="mb-4 -ml-2">
    <RouterLink :to="{ name: 'owner-transactions' }"><ArrowLeftIcon /> Riwayat transaksi</RouterLink>
  </Button>

  <ErrorAlert v-if="error" :message="error" />
  <div v-else-if="!trx" class="space-y-4">
    <Skeleton class="h-16 w-72" />
    <Skeleton class="h-72 w-full rounded-xl" />
  </div>

  <template v-else>
    <div class="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <Badge :variant="trx.type === 'SALE' ? 'success' : 'soft'" class="mb-2">
          {{ trx.type === 'SALE' ? 'Penjualan' : 'Restock' }}
        </Badge>
        <h1 class="font-mono text-2xl font-bold tracking-tight">{{ trx.code }}</h1>
        <p class="mt-1 text-sm text-muted-foreground">{{ formatDateTime(trx.createdAt) }} · dibuat oleh {{ trx.createdBy.name }}</p>
      </div>
      <Card v-if="grossProfit !== null" class="py-3">
        <CardContent class="px-5 text-right">
          <p class="text-[13px] font-semibold text-muted-foreground">Laba kotor transaksi</p>
          <p class="num text-xl font-extrabold text-success">{{ formatRupiah(grossProfit) }}</p>
        </CardContent>
      </Card>
    </div>
    <TransactionBody :trx="trx" />
  </template>
</template>
