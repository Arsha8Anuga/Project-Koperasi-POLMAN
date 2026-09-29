import { ref } from 'vue'

/**
 * Tema terang/gelap — ISI FILE INI IDENTIK di kedua app.
 * Pilihan disimpan di localStorage; kalau belum pernah dipilih, ikut pengaturan OS.
 * Class `dark` sudah dipasang sebelum Vue jalan (script kecil di index.html) supaya tidak berkedip.
 */
export type Theme = 'light' | 'dark'

const STORAGE_KEY = 'koperasi-theme'

function readStored(): Theme | null {
  try {
    const v = localStorage.getItem(STORAGE_KEY)
    return v === 'light' || v === 'dark' ? v : null
  } catch {
    return null
  }
}

function systemTheme(): Theme {
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

const theme = ref<Theme>(readStored() ?? systemTheme())

function apply(t: Theme) {
  document.documentElement.classList.toggle('dark', t === 'dark')
}
apply(theme.value)

// Ikuti perubahan tema OS selama user belum memilih sendiri.
window.matchMedia?.('(prefers-color-scheme: dark)').addEventListener?.('change', (e) => {
  if (readStored()) return
  theme.value = e.matches ? 'dark' : 'light'
  apply(theme.value)
})

export function useTheme() {
  function setTheme(t: Theme) {
    theme.value = t
    apply(t)
    try {
      localStorage.setItem(STORAGE_KEY, t)
    } catch {
      /* mode privat: abaikan */
    }
  }
  function toggle() {
    setTheme(theme.value === 'dark' ? 'light' : 'dark')
  }
  return { theme, setTheme, toggle }
}
