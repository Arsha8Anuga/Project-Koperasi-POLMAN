import { api } from './apiClient'
import type { AuditLog } from '@/types/api'

const MOCK = import.meta.env.VITE_MOCK_AUTH === 'true'

const mockLogs: AuditLog[] = [
  { id: 'a1', userName: 'Agus Wijaya', userRole: 'LOGISTIK', action: 'CREATE', entity: 'Product', detail: 'Buku Tulis', createdAt: new Date(Date.now() - 3 * 86400000).toISOString() },
  { id: 'a2', userName: 'Agus Wijaya', userRole: 'LOGISTIK', action: 'RESTOCK', entity: 'Product', detail: 'RST-0001 · Buku Tulis +50', createdAt: new Date(Date.now() - 2 * 86400000).toISOString() },
  { id: 'a3', userName: 'Dewi Lestari', userRole: 'ADMIN', action: 'CREATE', entity: 'User', detail: 'kasir1', createdAt: new Date(Date.now() - 86400000).toISOString() },
  { id: 'a4', userName: 'Siti Aminah', userRole: 'KASIR', action: 'SALE', entity: 'Transaction', detail: 'TRX-20260928-0001', createdAt: new Date(Date.now() - 3600000).toISOString() },
]

export interface AuditQuery {
  userName?: string
  entity?: string
  from?: string
  to?: string
}

export const auditApi = {
  async list(q: AuditQuery): Promise<AuditLog[]> {
    if (MOCK) {
      return mockLogs.filter((l) => {
        if (q.userName && !l.userName.toLowerCase().includes(q.userName.toLowerCase())) return false
        if (q.entity && l.entity !== q.entity) return false
        return true
      })
    }
    // TODO: cek nama query param di dokumen 04
    const res = await api.get<{ success: true; message: string; data: AuditLog[] }>('/audit-logs', { params: q })
    return res.data.data
  },
}