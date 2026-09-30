/**
 * URL gambar produk → URL yang bisa dipakai di <img>. ISI FILE INI IDENTIK di kedua frontend.
 *
 * Foto yang diunggah ke server disimpan sebagai `/api/v1/product-images/{id}` (tanpa domain), lalu
 * ditempelkan ke alamat API yang sedang dipakai: `/api/v1` di Docker (domain yang sama) atau
 * `http://localhost:8000/api/v1` saat `npm run dev`. URL luar (https://…) dipakai apa adanya.
 */
const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1').replace(/\/+$/, '')
const INTERNAL_PREFIX = '/api/v1/'

export function mediaUrl(url: string | null | undefined): string | null {
  if (!url) return null
  if (url.startsWith(INTERNAL_PREFIX)) return `${API_URL}/${url.slice(INTERNAL_PREFIX.length)}`
  return url
}

/** Foto hasil unggah (disimpan di server), bukan URL luar. */
export const isUploadedImage = (url: string | null | undefined) => !!url?.startsWith(`${INTERNAL_PREFIX}product-images/`)
