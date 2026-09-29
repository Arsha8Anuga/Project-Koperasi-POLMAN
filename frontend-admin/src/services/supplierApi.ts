import { api } from './apiClient'
import type { Supplier } from '@/types/api'

const MOCK = import.meta.env.VITE_MOCK_AUTH === 'true'

const mockSuppliers: Supplier[] = [
  { id: 's1', name: 'CV Sumber Rejeki', phone: '081234567890', address: 'Jl. Merdeka No. 1, Bandung' },
  { id: 's2', name: 'PT Distribusi Nusantara', phone: '081298765432', address: 'Jl. Asia Afrika No. 10, Bandung' },
]

export type SupplierInput = Pick<Supplier, 'name' | 'phone' | 'address'>

export const supplierApi = {
  async list(): Promise<Supplier[]> {
    if (MOCK) return mockSuppliers
    const res = await api.get<{ success: true; message: string; data: Supplier[] }>('/suppliers')
    return res.data.data
  },

  async create(input: SupplierInput): Promise<Supplier> {
    if (MOCK) {
      const sup: Supplier = { id: 's' + (mockSuppliers.length + 1), ...input }
      mockSuppliers.push(sup)
      return sup
    }
    const res = await api.post<{ success: true; message: string; data: Supplier }>('/suppliers', input)
    return res.data.data
  },

  async update(id: string, input: SupplierInput): Promise<Supplier> {
    if (MOCK) {
      const idx = mockSuppliers.findIndex((s) => s.id === id)
      if (idx === -1) throw new Error('Supplier tidak ditemukan')
      mockSuppliers[idx] = { ...mockSuppliers[idx], ...input }
      return mockSuppliers[idx]
    }
    const res = await api.put<{ success: true; message: string; data: Supplier }>(`/suppliers/${id}`, input)
    return res.data.data
  },

  async remove(id: string): Promise<void> {
    if (MOCK) {
      const idx = mockSuppliers.findIndex((s) => s.id === id)
      if (idx !== -1) mockSuppliers.splice(idx, 1)
      return
    }
    await api.delete(`/suppliers/${id}`)
  },
}