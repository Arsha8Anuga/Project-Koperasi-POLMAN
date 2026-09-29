import { api } from './apiClient'
import type { AdminUser, AdminUserInput } from '@/types/api'

const MOCK = import.meta.env.VITE_MOCK_AUTH === 'true'

const mockUsers: AdminUser[] = [
  { id: 'u1', name: 'Budi Santoso', username: 'owner', role: 'OWNER', isActive: true },
  { id: 'u2', name: 'Siti Aminah', username: 'kasir1', role: 'KASIR', isActive: true },
  { id: 'u3', name: 'Agus Wijaya', username: 'logistik', role: 'LOGISTIK', isActive: true },
  { id: 'u4', name: 'Dewi Lestari', username: 'admin', role: 'ADMIN', isActive: true },
]

export const userApi = {
  async list(): Promise<AdminUser[]> {
    if (MOCK) return mockUsers
    const res = await api.get<{ success: true; message: string; data: AdminUser[] }>('/users')
    return res.data.data
  },

  async create(input: AdminUserInput): Promise<AdminUser> {
    if (MOCK) {
      const user: AdminUser = { id: 'u' + (mockUsers.length + 1), name: input.name, username: input.username, role: input.role, isActive: true }
      mockUsers.push(user)
      return user
    }
    const res = await api.post<{ success: true; message: string; data: AdminUser }>('/users', input)
    return res.data.data
  },

  async update(id: string, input: AdminUserInput): Promise<AdminUser> {
    if (MOCK) {
      const idx = mockUsers.findIndex((u) => u.id === id)
      if (idx === -1) throw new Error('User tidak ditemukan')
      mockUsers[idx] = { ...mockUsers[idx], name: input.name, username: input.username, role: input.role }
      return mockUsers[idx]
    }
    const res = await api.put<{ success: true; message: string; data: AdminUser }>(`/users/${id}`, input)
    return res.data.data
  },

  async toggleActive(id: string): Promise<AdminUser> {
    if (MOCK) {
      const idx = mockUsers.findIndex((u) => u.id === id)
      if (idx === -1) throw new Error('User tidak ditemukan')
      mockUsers[idx] = { ...mockUsers[idx], isActive: !mockUsers[idx].isActive }
      return mockUsers[idx]
    }
    const res = await api.patch<{ success: true; message: string; data: AdminUser }>(`/users/${id}/status`)
    return res.data.data
  },

  async resetPassword(id: string): Promise<void> {
    if (MOCK) return
    await api.post(`/users/${id}/reset-password`)
  },
}