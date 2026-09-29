import { computed } from 'vue'
import { useTheme } from './useTheme'

/**
 * Warna chart mengikuti token shadcn di style.css (--chart-1..5, --border, --muted-foreground, ...),
 * dibaca dari CSS variable sehingga ikut berganti saat mode gelap.
 */
export function useChartTheme() {
  const { theme } = useTheme()

  return computed(() => {
    // `theme.value` dibaca supaya computed ini dihitung ulang saat tema berganti.
    const dark = theme.value === 'dark'
    const css = getComputedStyle(document.documentElement)
    const v = (name: string) => css.getPropertyValue(name).trim()
    return {
      dark,
      text: v('--muted-foreground'),
      grid: v('--border'),
      fg: v('--foreground'),
      surface: v('--card'),
      primary: v('--primary'),
      navy: v('--chart-1'),
      accent: v('--chart-2'),
      soft: v('--chart-3'),
      steel: v('--chart-4'),
      success: v('--success'),
      warning: v('--warning'),
      danger: v('--destructive'),
    }
  })
}
