import { onBeforeUnmount, onMounted } from 'vue'

/**
 * Menangkap hasil scanner barcode USB/Bluetooth ("keyboard wedge") di mana pun fokus berada.
 * ISI FILE INI IDENTIK di frontend-kasir & frontend-admin.
 *
 * Scanner "mengetik" belasan karakter sangat cepat (< ~35 ms per tombol) lalu menekan Enter;
 * manusia jauh lebih lambat. Kalau pola cepat itu terdeteksi:
 *  - Enter-nya ditahan (form tidak ter-submit),
 *  - karakter yang terlanjur masuk ke input yang sedang fokus dikembalikan seperti semula,
 *  - `onScan(kode)` dipanggil.
 *
 * Input yang menangani barcode sendiri (kolom barcode, pencarian POS) diberi atribut
 * `data-scan-input` supaya tidak diproses dua kali.
 */
export interface ScannerInputOptions {
  /** Panjang minimum kode yang dianggap scan. */
  minLength?: number
  /** Jeda maksimum antar tombol (ms) agar masih dianggap satu scan. */
  maxInterval?: number
}

type Editable = HTMLInputElement | HTMLTextAreaElement

function isEditable(el: EventTarget | null): el is Editable {
  return el instanceof HTMLInputElement || el instanceof HTMLTextAreaElement
}

export function useScannerInput(onScan: (code: string) => void, options: ScannerInputOptions = {}) {
  const minLength = options.minLength ?? 4
  const maxInterval = options.maxInterval ?? 35

  let buffer = ''
  let last = 0
  let snapshot: { el: Editable; value: string } | null = null

  function reset() {
    buffer = ''
    snapshot = null
  }

  function onKeydown(e: KeyboardEvent) {
    const target = e.target as HTMLElement | null
    if (target?.closest?.('[data-scan-input]')) return reset()
    if (e.ctrlKey || e.altKey || e.metaKey) return reset()

    const now = performance.now()
    const fast = now - last <= maxInterval
    last = now

    if (e.key === 'Enter') {
      if (fast && buffer.length >= minLength) {
        e.preventDefault()
        e.stopPropagation()
        const code = buffer
        if (snapshot && snapshot.el.value !== snapshot.value) {
          snapshot.el.value = snapshot.value
          snapshot.el.dispatchEvent(new Event('input', { bubbles: true })) // v-model ikut kembali
        }
        reset()
        onScan(code)
        return
      }
      return reset()
    }

    if (e.key.length !== 1) return // Shift, Tab, panah, dll.
    if (!fast) {
      // awal "ketikan" baru: catat isi input sebelum karakter ini masuk
      buffer = ''
      snapshot = isEditable(e.target) ? { el: e.target, value: e.target.value } : null
    }
    buffer += e.key
  }

  onMounted(() => window.addEventListener('keydown', onKeydown, true))
  onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown, true))
}
