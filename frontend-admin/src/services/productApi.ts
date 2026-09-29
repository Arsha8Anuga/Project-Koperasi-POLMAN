import { api } from './apiClient'
import type { Paginated, Product, ProductQuery } from '@/types/api'

const MOCK = import.meta.env.VITE_MOCK_AUTH === 'true'

const mockProducts: Product[] = [
  { id: '1', sku: 'ATK-001', name: 'Buku Tulis', categoryId: 'c1', categoryName: 'ATK', sellPrice: 4000, costPrice: 3000, lastPurchasePrice: 3000, stock: 48, minimumStock: 10, isActive: true, stockStatus: 'AMAN' },
  { id: '2', sku: 'ATK-002', name: 'Pulpen', categoryId: 'c1', categoryName: 'ATK', sellPrice: 2500, costPrice: 1800, lastPurchasePrice: 1800, stock: 3, minimumStock: 10, isActive: true, stockStatus: 'MENIPIS' },
  { id: '3', sku: 'MKN-001', name: 'Indomie Goreng', categoryId: 'c2', categoryName: 'Makanan', sellPrice: 3500, costPrice: 2900, lastPurchasePrice: 2900, stock: 0, minimumStock: 20, isActive: true, stockStatus: 'HABIS' },
]

export type ProductInput = Pick<Product, 'sku' | 'name' | 'categoryId' | 'sellPrice' | 'minimumStock'>

export const productApi = {
  async list(q: ProductQuery): Promise<Paginated<Product>> {
    if (MOCK) {
      const filtered = q.search
        ? mockProducts.filter((p) => p.name.toLowerCase().includes(q.search!.toLowerCase()))
        : mockProducts
      return {
        success: true,
        message: 'ok',
        data: filtered,
        meta: { page: q.page, limit: q.limit, total: filtered.length, totalPages: 1 },
      }
    }
    // TODO: cek nama query param di dokumen 04
    const res = await api.get<Paginated<Product>>('/products', { params: q })
    return res.data
  },

  async listAll(): Promise<Product[]> {
    if (MOCK) return mockProducts
    const res = await api.get<Paginated<Product>>('/products', { params: { page: 1, limit: 1000 } })
    return res.data.data
  },

  async get(id: string): Promise<Product> {
    if (MOCK) {
      const found = mockProducts.find((p) => p.id === id)
      if (!found) throw new Error('Produk tidak ditemukan')
      return found
    }
    const res = await api.get<{ success: true; message: string; data: Product }>(`/products/${id}`)
    return res.data.data
  },

  async create(input: ProductInput): Promise<Product> {
    if (MOCK) {
      const newProduct: Product = {
        id: String(mockProducts.length + 1),
        ...input,
        stock: 0,
        isActive: true,
        stockStatus: 'HABIS',
      }
      mockProducts.push(newProduct)
      return newProduct
    }
    // TODO: cek bentuk payload di dokumen 04
    const res = await api.post<{ success: true; message: string; data: Product }>('/products', input)
    return res.data.data
  },

  async update(id: string, input: ProductInput): Promise<Product> {
    if (MOCK) {
      const idx = mockProducts.findIndex((p) => p.id === id)
      if (idx === -1) throw new Error('Produk tidak ditemukan')
      mockProducts[idx] = { ...mockProducts[idx], ...input }
      return mockProducts[idx]
    }
    const res = await api.put<{ success: true; message: string; data: Product }>(`/products/${id}`, input)
    return res.data.data
  },
}