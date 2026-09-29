import axios from 'axios'
import router from '../router' // sesuaikan path sesuai lokasi router FE-1
import { useAuthStore } from '../stores/auth'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export class ApiException extends Error {
  status?: number
  code?: string
  details?: unknown[]

  constructor(status?: number, code?: string, message = 'Terjadi kesalahan jaringan', details?: unknown[]) {
    super(message)
    this.status = status
    this.code = code
    this.details = details
  }
}

apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    const status = err.response?.status
    const body = err.response?.data

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

export default apiClient