import { api } from './apiClient'
import type { Restock, RestockInput } from '@/types/api'

const MOCK = import.meta.env.VITE_MOCK_AUTH === 'true'
const mockRestocks: Restock[] = []

export const restockApi = {
  async list(): Promise<Restock[]> {
    if (MOCK) return mockRestocks
    const res = await api.get<{ success: true; message: string; data: Restock[] }>('/restocks')
    return res.data.data
  },

  async create(input: RestockInput, supplierName: string, itemNames: Record<string, string>): Promise<Restock> {
    if (MOCK) {
      const total = input.items.reduce((sum, i) => sum + i.qty * i.purchasePrice, 0)
      const restock: Restock = {
        id: String(mockRestocks.length + 1),
        code: `RST-${String(mockRestocks.length + 1).padStart(4, '0')}`,
        supplierId: input.supplierId,
        supplierName,
        note: input.note,
        items: input.items.map((i) => ({ ...i, productName: itemNames[i.productId] ?? i.productId })),
        total,
        createdAt: new Date().toISOString(),
      }
      mockRestocks.push(restock)
      return restock
    }
    // TODO: cek bentuk payload di dokumen 04/05 §5.3
    const res = await api.post<{ success: true; message: string; data: Restock }>('/restocks', input)
    return res.data.data
  },
}