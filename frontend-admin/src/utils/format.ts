export const formatRupiah = (n: number): string =>
  'Rp ' + new Intl.NumberFormat('id-ID').format(n)

export const formatDateTime = (iso: string): string =>
  new Intl.DateTimeFormat('id-ID', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Jakarta',
  }).format(new Date(iso))