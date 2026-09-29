import { api } from './apiClient'
import type { Category } from '@/types/api'

const MOCK = import.meta.env.VITE_MOCK_AUTH === 'true'

const mockCategories: Category[] = [
  { id: 'c1', name: 'ATK' },
  { id: 'c2', name: 'Makanan' },
  { id: 'c3', name: 'Minuman' },
]

export const categoryApi = {
  async list(): Promise<Category[]> {
    if (MOCK) return mockCategories
    const res = await api.get<{ success: true; message: string; data: Category[] }>('/categories')
    return res.data.data
  },

  async create(name: string): Promise<Category> {
    if (MOCK) {
      const cat: Category = { id: 'c' + (mockCategories.length + 1), name }
      mockCategories.push(cat)
      return cat
    }
    const res = await api.post<{ success: true; message: string; data: Category }>('/categories', { name })
    return res.data.data
  },

  async update(id: string, name: string): Promise<Category> {
    if (MOCK) {
      const idx = mockCategories.findIndex((c) => c.id === id)
      if (idx === -1) throw new Error('Kategori tidak ditemukan')
      mockCategories[idx] = { ...mockCategories[idx], name }
      return mockCategories[idx]
    }
    const res = await api.put<{ success: true; message: string; data: Category }>(`/categories/${id}`, { name })
    return res.data.data
  },

  async remove(id: string): Promise<void> {
    if (MOCK) {
      const idx = mockCategories.findIndex((c) => c.id === id)
      if (idx !== -1) mockCategories.splice(idx, 1)
      return
    }
    await api.delete(`/categories/${id}`)
  },
}