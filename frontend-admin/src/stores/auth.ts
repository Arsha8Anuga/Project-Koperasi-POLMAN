import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { api, TOKEN_KEY } from '@/services/apiClient'
import type { ApiResponse, LoginData, Role, User } from '@/types/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))
  const user = ref<Pick<User, 'id' | 'name' | 'username' | 'role'> | null>(null)
  const isAuthenticated = computed(() => !!token.value)

  /** Melempar ApiException kalau gagal — pesannya dari backend dan siap ditampilkan. */
  async function login(username: string, password: string) {
    const res = await api.post<ApiResponse<LoginData>>('/auth/login', { username, password, app: 'ADMIN' })
    token.value = res.data.data.token
    user.value = res.data.data.user
    localStorage.setItem(TOKEN_KEY, token.value)
  }

  /** Dipanggil guard setelah refresh halaman: token masih ada, data user belum. */
  async function fetchMe() {
    const res = await api.get<ApiResponse<User>>('/auth/me')
    user.value = res.data.data
  }

  async function logout() {
    try {
      if (token.value) await api.post('/auth/logout')
    } catch {
      /* token sudah tidak berlaku: tetap keluar */
    }
    clear()
  }

  function clear() {
    token.value = null
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
  }

  const hasRole = (...roles: Role[]) => !!user.value && roles.includes(user.value.role)

  return { token, user, isAuthenticated, login, fetchMe, logout, clear, hasRole }
})
