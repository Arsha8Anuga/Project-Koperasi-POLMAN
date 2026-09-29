import { api } from './api'
import type { ApiResponse, MemberLookup, Paginated, Sale, SaleRequest } from '@/types'

export const salesApi = {
  async create(body: SaleRequest): Promise<Sale> {
    const res = await api.post<ApiResponse<Sale>>('/sales', body)
    return res.data.data
  },

  async mine(params: { page: number; limit: number; from?: string; to?: string }): Promise<Paginated<Sale>> {
    const res = await api.get<Paginated<Sale>>('/sales/mine', { params })
    return res.data
  },

  async get(id: string): Promise<Sale> {
    const res = await api.get<ApiResponse<Sale>>(`/sales/${id}`)
    return res.data.data
  },

  async lookupMember(memberNumber: string): Promise<MemberLookup> {
    const res = await api.get<ApiResponse<MemberLookup>>(`/members/lookup/${encodeURIComponent(memberNumber)}`)
    return res.data.data
  },
}
