const fmt = new Intl.DateTimeFormat('id-ID', {
  timeZone: 'Asia/Jakarta',
  day: '2-digit',
  month: 'short',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
  hour12: false,
})

// "2026-09-28T03:42:10Z" -> "28 Sep 2026 10.42" (WIB)
export function formatDateTime(iso: string): string {
  const p = Object.fromEntries(fmt.formatToParts(new Date(iso)).map((x) => [x.type, x.value]))
  return `${p.day} ${p.month} ${p.year} ${p.hour}.${p.minute}`
}