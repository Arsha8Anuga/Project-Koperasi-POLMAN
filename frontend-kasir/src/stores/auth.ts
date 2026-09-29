import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { api, TOKEN_KEY, USER_KEY } from '@/services/api'
import type { ApiResponse, LoginData, UserBrief } from '@/types'

function readUser(): UserBrief | null {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY) || 'null') as UserBrief | null
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))
  const user = ref<UserBrief | null>(readUser())
  const isAuthenticated = computed(() => !!token.value)

  /** Melempar ApiException kalau gagal — pesannya dari backend dan siap ditampilkan. */
  async function login(username: string, password: string) {
    const res = await api.post<ApiResponse<LoginData>>('/auth/login', { username, password, app: 'KASIR' })
    token.value = res.data.data.token
    user.value = res.data.data.user
    localStorage.setItem(TOKEN_KEY, token.value)
    localStorage.setItem(USER_KEY, JSON.stringify(user.value))
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
    localStorage.removeItem(USER_KEY)
  }

  return { token, user, isAuthenticated, login, logout, clear }
})
