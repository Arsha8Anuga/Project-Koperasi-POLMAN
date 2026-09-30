/**
 * Memperkecil foto di browser sebelum diunggah: sisi terpanjang maks 1024 px, WebP (atau JPEG kalau
 * browser tidak bisa membuat WebP, mis. Safari lama). Foto HP 4–8 MB biasanya jadi 80–250 KB.
 * Orientasi EXIF (foto HP yang "miring") ikut dibetulkan oleh createImageBitmap.
 */
export const MAX_SOURCE_BYTES = 20 * 1024 * 1024
export const MAX_UPLOAD_BYTES = 1_500_000 // sama dengan batas backend

async function decode(file: Blob): Promise<ImageBitmap | HTMLImageElement> {
  if ('createImageBitmap' in window) {
    try {
      return await createImageBitmap(file, { imageOrientation: 'from-image' })
    } catch {
      /* format tidak didukung createImageBitmap (mis. HEIC di beberapa browser) → coba <img> */
    }
  }
  const url = URL.createObjectURL(file)
  try {
    const img = new Image()
    img.src = url
    await img.decode()
    return img
  } finally {
    URL.revokeObjectURL(url)
  }
}

function toBlob(canvas: HTMLCanvasElement, type: string, quality: number): Promise<Blob | null> {
  return new Promise((resolve) => canvas.toBlob(resolve, type, quality))
}

export async function compressImage(file: File, maxSide = 1024): Promise<Blob> {
  if (!file.type.startsWith('image/')) throw new Error('File yang dipilih bukan gambar')
  if (file.size > MAX_SOURCE_BYTES) throw new Error('Foto terlalu besar (maks 20 MB)')

  let source: ImageBitmap | HTMLImageElement
  try {
    source = await decode(file)
  } catch {
    throw new Error('Format foto tidak bisa dibaca browser ini. Gunakan JPG, PNG, atau WebP.')
  }
  const w = 'naturalWidth' in source ? source.naturalWidth : source.width
  const h = 'naturalHeight' in source ? source.naturalHeight : source.height
  const scale = Math.min(1, maxSide / Math.max(w, h))
  const canvas = document.createElement('canvas')
  canvas.width = Math.max(1, Math.round(w * scale))
  canvas.height = Math.max(1, Math.round(h * scale))
  const ctx = canvas.getContext('2d')
  if (!ctx) throw new Error('Browser tidak mendukung pemrosesan gambar')
  ctx.fillStyle = '#ffffff' // PNG transparan → latar putih (JPEG tidak punya transparansi)
  ctx.fillRect(0, 0, canvas.width, canvas.height)
  ctx.drawImage(source, 0, 0, canvas.width, canvas.height)
  if ('close' in source) source.close()

  let blob = await toBlob(canvas, 'image/webp', 0.82)
  if (!blob || blob.type !== 'image/webp') blob = await toBlob(canvas, 'image/jpeg', 0.85)
  if (!blob) throw new Error('Gagal memproses foto')
  if (blob.size > MAX_UPLOAD_BYTES) blob = (await toBlob(canvas, 'image/jpeg', 0.6)) ?? blob
  if (blob.size > MAX_UPLOAD_BYTES) throw new Error('Foto masih terlalu besar setelah diperkecil')
  return blob
}
