import axios, { AxiosError } from 'axios'

/** Error dari backend dalam bentuk yang enak dipakai UI (dokumen 04 §2). */
export class ApiException extends Error {
  status: number | undefined
  code: string | undefined
  details: { field?: string; message?: string }[]

  constructor(
    status: number | undefined,
    code: string | undefined,
    message: string,
    details: { field?: string; message?: string }[] = [],
  ) {
    super(message)
    this.status = status
    this.code = code
    this.details = details
  }

  /** {field: pesan} dari error validasi / duplikat, untuk ditaruh di bawah input. */
  fieldErrors(): Record<string, string> {
    const out: Record<string, string> = {}
    for (const d of this.details) if (d.field) out[d.field] = d.message ?? this.message
    return out
  }
}

export const TOKEN_KEY = 'admin_token'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 20000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

type ErrorBody = { message?: string; error?: { code?: string; details?: { field?: string; message?: string }[] } }

api.interceptors.response.use(
  (res) => res,
  async (err: AxiosError<ErrorBody>) => {
    const status = err.response?.status
    const body = err.response?.data
    const isLogin = err.config?.url?.includes('/auth/login')

    if (status === 401 && !isLogin) {
      // Token tidak berlaku → keluar. Import router secara lazy supaya tidak circular.
      localStorage.removeItem(TOKEN_KEY)
      const { default: router } = await import('@/router')
      const current = router.currentRoute.value
      if (current.name !== 'login') router.push({ name: 'login', query: { redirect: current.fullPath } })
    } else if (status === 403 && ['FORBIDDEN', 'ACCOUNT_INACTIVE'].includes(body?.error?.code ?? '') && !isLogin) {
      const { default: router } = await import('@/router')
      if (body?.error?.code === 'ACCOUNT_INACTIVE') {
        localStorage.removeItem(TOKEN_KEY)
        router.push({ name: 'login' })
      } else {
        router.push({ name: 'forbidden' })
      }
    }

    const message = body?.message ?? (err.response ? 'Terjadi kesalahan pada server' : 'Tidak dapat terhubung ke server')
    return Promise.reject(new ApiException(status, body?.error?.code, message, body?.error?.details ?? []))
  },
)

export function errorMessage(e: unknown, fallback = 'Terjadi kesalahan'): string {
  return e instanceof Error && e.message ? e.message : fallback
}

/** Buang parameter kosong supaya URL query bersih. */
export function clean<T extends object>(params: T): Partial<T> {
  return Object.fromEntries(
    Object.entries(params).filter(([, v]) => v !== '' && v !== null && v !== undefined),
  ) as Partial<T>
}
