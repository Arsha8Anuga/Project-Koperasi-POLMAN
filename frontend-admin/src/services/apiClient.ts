import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import type { ApiError } from '@/types/api'

export class ApiException extends Error {
  status?: number
  code?: string
  details?: unknown[]
  constructor(status: number | undefined, code: string | undefined, message: string, details?: unknown[]) {
    super(message)
    this.status = status
    this.code = code
    this.details = details
  }
}

export const api = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL })

api.interceptors.request.use((cfg) => {
  const token = useAuthStore().token
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const status = err.response?.status as number | undefined
    const body = err.response?.data as ApiError | undefined
    // import router secara lazy supaya tidak circular import
    const { default: router } = await import('@/router')
    if (status === 401) {
      useAuthStore().logout()
      router.push('/login')
    } else if (status === 403) {
      router.push('/403')
    }
    return Promise.reject(
      new ApiException(status, body?.error?.code, body?.message ?? 'Terjadi kesalahan jaringan', body?.error?.details),
    )
  },
)