import axios, { AxiosError } from 'axios'

/** Error dari backend dalam bentuk yang enak dipakai UI (dokumen 04 §2). */
export class ApiException extends Error {
  status: number | undefined
  code: string | undefined
  details: unknown[]

  constructor(status: number | undefined, code: string | undefined, message: string, details: unknown[] = []) {
    super(message)
    this.status = status
    this.code = code
    this.details = details
  }
}

export const TOKEN_KEY = 'kasir_token'
export const USER_KEY = 'kasir_user'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  async (err: AxiosError<{ message?: string; error?: { code?: string; details?: unknown[] } }>) => {
    const status = err.response?.status
    const body = err.response?.data
    const isLogin = err.config?.url?.includes('/auth/login')

    // Token kadaluarsa/invalid → keluar. KECUALI saat login (401 = password salah, tampilkan saja).
    if (status === 401 && !isLogin) {
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
      const { default: router } = await import('@/router')
      if (router.currentRoute.value.name !== 'login') router.push({ name: 'login' })
    }

    const message = body?.message ?? (err.response ? 'Terjadi kesalahan pada server' : 'Tidak dapat terhubung ke server')
    return Promise.reject(new ApiException(status, body?.error?.code, message, body?.error?.details ?? []))
  },
)

export function errorMessage(e: unknown, fallback = 'Terjadi kesalahan'): string {
  return e instanceof Error && e.message ? e.message : fallback
}
