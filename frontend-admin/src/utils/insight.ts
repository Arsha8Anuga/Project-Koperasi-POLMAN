/** Label & format untuk hasil AI engine. */

export const MODEL_LABEL: Record<string, string> = {
  holt_winters: 'Holt-Winters (pola mingguan)',
  moving_average: 'Rata-rata 7 hari',
  croston: 'Croston (penjualan jarang)',
}

export const modelLabel = (m: string) => MODEL_LABEL[m] ?? m

export function formatDays(days: number | null | undefined): string {
  if (days === null || days === undefined) return 'Tidak diperkirakan habis'
  if (days <= 0) return 'Sudah habis'
  if (days > 60) return '> 60 hari'
  return `±${days.toLocaleString('id-ID', { maximumFractionDigits: 1 })} hari`
}

export const percent = (v: number | null | undefined, digits = 0) =>
  v === null || v === undefined ? '—' : `${(v * 100).toLocaleString('id-ID', { maximumFractionDigits: digits })}%`

/** Tingkat urgensi relatif terhadap lead time supplier (bawaan 3 hari) dan periode restock (7 hari). */
export function urgency(days: number | null, leadTime = 3, review = 7): 'danger' | 'warning' | 'ok' {
  if (days === null) return 'ok'
  if (days <= leadTime) return 'danger'
  if (days <= leadTime + review) return 'warning'
  return 'ok'
}
