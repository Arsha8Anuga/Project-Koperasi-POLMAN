import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { api } from '@/services/apiClient'
import type { ApiResponse, Role, User } from '@/types/api'

const TOKEN_KEY = 'admin_token'
const MOCK_USER_KEY = 'admin_mock_user'
const MOCK = import.meta.env.VITE_MOCK_AUTH === 'true'

function read(key: string): string | null {
  try { return localStorage.getItem(key) } catch { return null }
}
function write(key: string, value: string | null) {
  try { value ? localStorage.setItem(key, value) : localStorage.removeItem(key) } catch { /* abaikan */ }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(read(TOKEN_KEY))
  const user = ref<User | null>(null)
  const isAuthenticated = computed(() => !!token.value)

  async function login(username: string, password: string) {
    if (MOCK) {
      // SEMENTARA: username owner / logistik / admin, password bebas
      const role = username.toUpperCase() as Role
      if (!['OWNER', 'LOGISTIK', 'ADMIN'].includes(role)) {
        throw new Error('Mode mock: pakai username owner, logistik, atau admin')
      }
      token.value = 'mock-token'
      user.value = { id: role.toLowerCase(), name: `Demo ${role}`, username, role }
      write(TOKEN_KEY, token.value)
      write(MOCK_USER_KEY, JSON.stringify(user.value))
      return
    }
    // TODO: cek nama field & bentuk response di dokumen 04
    const res = await api.post<ApiResponse<{ token: string; user: User }>>('/auth/login', {
      username, password, app: 'ADMIN',
    })
    token.value = res.data.data.token
    user.value = res.data.data.user
    write(TOKEN_KEY, token.value)
  }

  async function fetchMe() {
    if (MOCK) {
      const saved = read(MOCK_USER_KEY)
      if (!saved) throw new Error('Tidak ada sesi')
      user.value = JSON.parse(saved) as User
      return
    }
    const res = await api.get<ApiResponse<User>>('/auth/me')
    user.value = res.data.data
  }

  function logout() {
    token.value = null
    user.value = null
    write(TOKEN_KEY, null)
    write(MOCK_USER_KEY, null)
  }

  const hasRole = (...roles: Role[]) => !!user.value && roles.includes(user.value.role)

  return { token, user, isAuthenticated, login, fetchMe, logout, hasRole }
})