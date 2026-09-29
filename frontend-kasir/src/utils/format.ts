/** Format tampilan — ISI FILE INI IDENTIK di kedua app. Semua waktu ditampilkan dalam WIB. */

const rupiahFmt = new Intl.NumberFormat('id-ID')
const dateTimeFmt = new Intl.DateTimeFormat('id-ID', {
  timeZone: 'Asia/Jakarta',
  day: '2-digit',
  month: 'short',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
  hour12: false,
})
const dateFmt = new Intl.DateTimeFormat('id-ID', {
  timeZone: 'Asia/Jakarta',
  day: '2-digit',
  month: 'short',
  year: 'numeric',
})

export const formatRupiah = (n: number | null | undefined): string => 'Rp ' + rupiahFmt.format(n ?? 0)

export const formatNumber = (n: number | null | undefined): string => rupiahFmt.format(n ?? 0)

/** "2026-09-28T03:42:10Z" → "28 Sep 2026 10.42" (WIB) */
export const formatDateTime = (iso: string | null | undefined): string =>
  iso ? dateTimeFmt.format(new Date(iso)) : '-'

/** "2026-09-28" atau ISO → "28 Sep 2026" */
export const formatDate = (value: string | null | undefined): string => {
  if (!value) return '-'
  const d = value.length === 10 ? new Date(`${value}T00:00:00+07:00`) : new Date(value)
  return dateFmt.format(d)
}

/** Tanggal hari ini di WIB, format YYYY-MM-DD (untuk query from/to). */
export function todayWib(offsetDays = 0): string {
  const d = new Date(Date.now() + offsetDays * 86_400_000)
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Jakarta' }).format(d)
}
