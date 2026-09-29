import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
} from 'chart.js'

// Didaftarkan sekali untuk semua chart.
ChartJS.register(BarElement, CategoryScale, Filler, Legend, LinearScale, LineElement, PointElement, Tooltip)
ChartJS.defaults.font.family = '"Plus Jakarta Sans", ui-sans-serif, system-ui, sans-serif'
ChartJS.defaults.font.size = 12
ChartJS.defaults.plugins.legend.labels.usePointStyle = true
ChartJS.defaults.plugins.legend.labels.boxWidth = 8
ChartJS.defaults.plugins.tooltip.padding = 10
ChartJS.defaults.plugins.tooltip.cornerRadius = 8

/** 1.250.000 → "1,3 jt" untuk sumbu Y supaya tidak sesak. */
export function compactRupiah(v: number | string): string {
  const n = Number(v)
  const abs = Math.abs(n)
  if (abs >= 1_000_000_000) return `${(n / 1_000_000_000).toLocaleString('id-ID', { maximumFractionDigits: 1 })} M`
  if (abs >= 1_000_000) return `${(n / 1_000_000).toLocaleString('id-ID', { maximumFractionDigits: 1 })} jt`
  if (abs >= 1_000) return `${(n / 1_000).toLocaleString('id-ID', { maximumFractionDigits: 0 })} rb`
  return n.toLocaleString('id-ID')
}

/** Label periode dari backend → label pendek yang enak dibaca di sumbu X. */
export function periodLabel(period: string, granularity: string): string {
  if (granularity === 'year') return period
  if (granularity === 'month') {
    const [y = 1970, m = 1] = period.split('-').map(Number)
    return new Date(y, m - 1, 1).toLocaleDateString('id-ID', { month: 'short', year: '2-digit' })
  }
  const d = new Date(`${period}T00:00:00`)
  const txt = d.toLocaleDateString('id-ID', { day: 'numeric', month: 'short' })
  return granularity === 'week' ? `Mg ${txt}` : txt
}
