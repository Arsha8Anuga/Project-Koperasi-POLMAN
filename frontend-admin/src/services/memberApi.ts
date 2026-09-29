import { api } from './apiClient'
import type { Member, MemberInput } from '@/types/api'

const MOCK = import.meta.env.VITE_MOCK_AUTH === 'true'

const mockMembers: Member[] = [
  { id: 'mb1', memberNumber: 'AGT-0001', name: 'Rina Marlina', phone: '081211112222', isActive: true },
  { id: 'mb2', memberNumber: 'AGT-0002', name: 'Joko Prasetyo', phone: '081233334444', isActive: true },
]

export const memberApi = {
  async list(): Promise<Member[]> {
    if (MOCK) return mockMembers
    const res = await api.get<{ success: true; message: string; data: Member[] }>('/members')
    return res.data.data
  },

  async create(input: MemberInput): Promise<Member> {
    if (MOCK) {
      const member: Member = { id: 'mb' + (mockMembers.length + 1), ...input, isActive: true }
      mockMembers.push(member)
      return member
    }
    const res = await api.post<{ success: true; message: string; data: Member }>('/members', input)
    return res.data.data
  },

  async update(id: string, input: MemberInput): Promise<Member> {
    if (MOCK) {
      const idx = mockMembers.findIndex((m) => m.id === id)
      if (idx === -1) throw new Error('Anggota tidak ditemukan')
      mockMembers[idx] = { ...mockMembers[idx], ...input }
      return mockMembers[idx]
    }
    const res = await api.put<{ success: true; message: string; data: Member }>(`/members/${id}`, input)
    return res.data.data
  },

  async remove(id: string): Promise<void> {
    if (MOCK) {
      const idx = mockMembers.findIndex((m) => m.id === id)
      if (idx !== -1) mockMembers.splice(idx, 1)
      return
    }
    await api.delete(`/members/${id}`)
  },
}