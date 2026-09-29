import { api } from './api'
import type { ApiResponse, Category, Paginated, Product } from '@/types'

export interface ProductQuery {
  search?: string
  categoryId?: string
  page?: number
  limit?: number
}

export const catalogApi = {
  async products(q: ProductQuery): Promise<Paginated<Product>> {
    const params = { sort: 'name', limit: 100, ...q, search: q.search || undefined, categoryId: q.categoryId || undefined }
    const res = await api.get<Paginated<Product>>('/products', { params })
    return res.data
  },

  async categories(): Promise<Category[]> {
    const res = await api.get<ApiResponse<Category[]>>('/categories', { params: { isActive: true } })
    return res.data.data
  },
}
