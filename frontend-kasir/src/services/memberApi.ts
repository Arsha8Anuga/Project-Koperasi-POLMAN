import { api } from './api'
import type { ApiResponse, Member, MemberCreate, MemberLookup } from '@/types'

export const memberApi = {
  /** Cari anggota aktif berdasarkan nomor (KOP-001). 404 kalau tidak ada / nonaktif. */
  async lookup(memberNumber: string): Promise<MemberLookup> {
    const res = await api.get<ApiResponse<MemberLookup>>(`/members/lookup/${encodeURIComponent(memberNumber)}`)
    return res.data.data
  },

  /** Kasir boleh mendaftarkan anggota baru; ubah & nonaktifkan hanya lewat admin. */
  async register(body: MemberCreate): Promise<Member> {
    const res = await api.post<ApiResponse<Member>>('/members', body)
    return res.data.data
  },
}
