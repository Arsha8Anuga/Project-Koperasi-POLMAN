<script setup lang="ts">
/**
 * Pemindai barcode lewat kamera — ISI FILE INI IDENTIK di frontend-kasir & frontend-admin.
 *
 * Kamera apa pun yang dikenali browser bisa dipilih: webcam laptop, webcam USB, HP yang dipakai
 * sebagai webcam (DroidCam/Iriun/mode webcam Android), atau kamera HP/tablet saat aplikasi dibuka
 * langsung di perangkat itu. Pilihan kamera diingat di localStorage.
 * Decoding memakai ZXing (algoritma baca barcode biasa, bukan model AI). Kamera hanya jalan di HTTPS/localhost.
 *
 *   <BarcodeScanner v-model:open="scanOpen" continuous @detected="onCode" />
 */
import { BarcodeFormat, BrowserMultiFormatReader, type IScannerControls } from '@zxing/browser'
import { CameraOffIcon, ScanBarcodeIcon } from '@lucide/vue'
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
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
import { NativeSelect, NativeSelectOption } from '@/components/ui/native-select'
import { Spinner } from '@/components/ui/spinner'

const props = withDefaults(
  defineProps<{
    title?: string
    /** true = tetap terbuka setelah berhasil (scan beberapa barang berturut-turut). */
    continuous?: boolean
  }>(),
  { title: 'Scan barcode', continuous: false },
)
const open = defineModel<boolean>('open', { required: true })
const emit = defineEmits<{ detected: [code: string] }>()

const STORAGE_KEY = 'koperasi-camera'
const SAME_CODE_DELAY = 1500 // ms: kode sama tidak dikirim dua kali selama barang masih di depan kamera

const video = ref<HTMLVideoElement | null>(null)
const devices = ref<MediaDeviceInfo[]>([])
const deviceId = ref(readStored())
const starting = ref(false)
const error = ref('')
const lastCode = ref('')
const flash = ref(false)

let controls: IScannerControls | null = null
let lastAt = 0

const reader = new BrowserMultiFormatReader(undefined, { delayBetweenScanAttempts: 120, delayBetweenScanSuccess: 400 })
reader.possibleFormats = [
  BarcodeFormat.EAN_13,
  BarcodeFormat.EAN_8,
  BarcodeFormat.UPC_A,
  BarcodeFormat.UPC_E,
  BarcodeFormat.CODE_128,
  BarcodeFormat.CODE_39,
  BarcodeFormat.ITF,
  BarcodeFormat.QR_CODE,
]

function readStored(): string {
  try {
    return localStorage.getItem(STORAGE_KEY) ?? ''
  } catch {
    return ''
  }
}

function store(id: string) {
  try {
    if (id) localStorage.setItem(STORAGE_KEY, id)
    else localStorage.removeItem(STORAGE_KEY)
  } catch {
    /* mode privat: abaikan */
  }
}

function stop() {
  controls?.stop()
  controls = null
}

function beep() {
  try {
    const ctx = new AudioContext()
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()
    osc.frequency.value = 1320
    gain.gain.value = 0.08
    osc.connect(gain).connect(ctx.destination)
    osc.start()
    osc.stop(ctx.currentTime + 0.09)
    osc.onended = () => ctx.close()
  } catch {
    /* audio tidak tersedia: abaikan */
  }
}

function describe(e: unknown): string {
  const name = e instanceof DOMException ? e.name : ''
  if (name === 'NotAllowedError') return 'Izin kamera ditolak. Izinkan kamera untuk situs ini di pengaturan browser.'
  if (name === 'NotFoundError' || name === 'OverconstrainedError') return 'Kamera tidak ditemukan.'
  if (name === 'NotReadableError') return 'Kamera sedang dipakai aplikasi lain.'
  return 'Kamera tidak bisa dibuka.'
}

async function start() {
  stop()
  error.value = ''
  if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia) {
    error.value = 'Kamera hanya bisa dipakai lewat HTTPS (atau localhost).'
    return
  }
  starting.value = true
  // elemen <video> baru ada setelah isi dialog ter-render
  for (let i = 0; i < 10 && !video.value; i++) await nextTick()
  const size = { width: { ideal: 1280 }, height: { ideal: 720 } }
  const constraints: MediaStreamConstraints = {
    audio: false,
    video: deviceId.value ? { deviceId: { exact: deviceId.value }, ...size } : { facingMode: { ideal: 'environment' }, ...size },
  }
  try {
    controls = await reader.decodeFromConstraints(constraints, video.value ?? undefined, (result) => {
      if (!result) return
      const code = result.getText().trim()
      const now = Date.now()
      if (!code || (code === lastCode.value && now - lastAt < SAME_CODE_DELAY)) return
      lastCode.value = code
      lastAt = now
      beep()
      flash.value = true
      setTimeout(() => (flash.value = false), 250)
      emit('detected', code)
      if (!props.continuous) open.value = false
    })
    // label kamera baru tersedia setelah izin diberikan
    devices.value = await BrowserMultiFormatReader.listVideoInputDevices()
  } catch (e) {
    if (deviceId.value && e instanceof DOMException && ['NotFoundError', 'OverconstrainedError'].includes(e.name)) {
      // kamera yang diingat sudah tidak ada (HP dicabut, dsb.): coba kamera bawaan
      deviceId.value = ''
      store('')
      starting.value = false
      return start()
    }
    error.value = describe(e)
  } finally {
    starting.value = false
  }
}

function onDeviceChange(v: unknown) {
  deviceId.value = typeof v === 'string' ? v : ''
  store(deviceId.value)
  start()
}

watch(
  open,
  (v) => {
    if (v) {
      lastCode.value = ''
      start()
    } else stop()
  },
  { immediate: true },
)

onBeforeUnmount(stop)
</script>

<template>
  <Dialog v-model:open="open">
    <DialogContent class="sm:max-w-lg">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2"><ScanBarcodeIcon class="size-5" /> {{ title }}</DialogTitle>
        <DialogDescription>
          Arahkan barcode ke kamera sampai terdengar bunyi.
          <template v-if="continuous"> Dialog tetap terbuka untuk barang berikutnya.</template>
        </DialogDescription>
      </DialogHeader>

      <NativeSelect
        v-if="devices.length > 1"
        :model-value="deviceId"
        class="w-full"
        aria-label="Pilih kamera"
        @update:model-value="onDeviceChange"
      >
        <NativeSelectOption value="">Kamera bawaan (otomatis)</NativeSelectOption>
        <NativeSelectOption v-for="(d, i) in devices" :key="d.deviceId" :value="d.deviceId">
          {{ d.label || `Kamera ${i + 1}` }}
        </NativeSelectOption>
      </NativeSelect>

      <div class="relative aspect-video overflow-hidden rounded-lg bg-black">
        <video ref="video" class="size-full object-cover" muted playsinline />
        <!-- garis bidik -->
        <div
          v-if="!error"
          class="pointer-events-none absolute inset-x-8 top-1/2 h-24 -translate-y-1/2 rounded-md border-2 transition-colors"
          :class="flash ? 'border-success bg-success/20' : 'border-white/70'"
        />
        <div v-if="starting" class="absolute inset-0 flex items-center justify-center gap-2 text-sm text-white">
          <Spinner /> Membuka kamera…
        </div>
        <div v-if="error" class="absolute inset-0 flex flex-col items-center justify-center gap-2 p-6 text-center text-sm text-white">
          <CameraOffIcon class="size-8 opacity-70" />
          {{ error }}
        </div>
      </div>

      <Alert v-if="lastCode && continuous" variant="success">
        <AlertDescription>
          Terakhir: <span class="font-mono font-semibold">{{ lastCode }}</span>
        </AlertDescription>
      </Alert>

      <DialogFooter>
        <Button v-if="error" variant="outline" @click="start">Coba lagi</Button>
        <Button variant="secondary" @click="open = false">{{ continuous ? 'Selesai' : 'Tutup' }}</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
