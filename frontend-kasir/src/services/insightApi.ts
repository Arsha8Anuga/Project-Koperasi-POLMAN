import { api } from './api'
import type { ApiResponse, Suggestion } from '@/types'

export const insightApi = {
  /** Saran dari AI engine untuk isi keranjang. Kosong kalau engine belum pernah menghitung. */
  async frequentlyBought(productIds: string[], limit = 3): Promise<Suggestion[]> {
    if (!productIds.length) return []
    const res = await api.get<ApiResponse<{ generatedAt: string | null; items: Suggestion[] }>>(
      '/insights/frequently-bought',
      { params: { productIds: productIds.join(','), limit } },
    )
    return res.data.data.items
  },
}
