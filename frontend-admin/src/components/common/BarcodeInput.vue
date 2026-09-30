<script setup lang="ts">
import { ScanBarcodeIcon } from '@lucide/vue'
import { ref } from 'vue'
import BarcodeScanner from '@/components/common/BarcodeScanner.vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Spinner } from '@/components/ui/spinner'

/**
 * Kolom "ketik atau scan barcode" + tombol kamera. Enter / hasil kamera → emit `submit(kode)`.
 * Scanner USB juga bisa diarahkan ke sini (kolom ini bertanda data-scan-input, jadi
 * useScannerInput global tidak memprosesnya dua kali).
 */
withDefaults(
  defineProps<{ placeholder?: string; loading?: boolean; continuous?: boolean; scannerTitle?: string }>(),
  { placeholder: 'Ketik atau scan barcode / SKU, lalu Enter', continuous: false, scannerTitle: 'Scan barcode' },
)
const emit = defineEmits<{ submit: [code: string] }>()

const code = ref('')
const scanOpen = ref(false)

function submit() {
  const v = code.value.trim()
  if (!v) return
  emit('submit', v)
  code.value = ''
}
</script>

<template>
  <div class="flex w-full gap-2">
    <div class="relative flex-1">
      <ScanBarcodeIcon class="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
      <Input
        v-model="code"
        data-scan-input
        class="pl-9 font-mono"
        :placeholder="placeholder"
        :aria-label="placeholder"
        autocomplete="off"
        @keydown.enter.prevent="submit"
      />
      <Spinner v-if="loading" class="absolute top-1/2 right-3 -translate-y-1/2 text-muted-foreground" />
    </div>
    <Button type="button" variant="outline" title="Scan pakai kamera" @click="scanOpen = true">
      <ScanBarcodeIcon /> <span class="hidden sm:inline">Kamera</span>
    </Button>
  </div>
  <BarcodeScanner v-model:open="scanOpen" :title="scannerTitle" :continuous="continuous" @detected="emit('submit', $event)" />
</template>
