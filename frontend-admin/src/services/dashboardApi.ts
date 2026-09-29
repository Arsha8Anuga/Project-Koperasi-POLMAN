import { api } from './apiClient'
import type { DashboardSummary } from '@/types/api'

const MOCK = import.meta.env.VITE_MOCK_AUTH === 'true'

const mockSummary: Record<string, DashboardSummary> = {
  OWNER: { todaySales: 285000, todayTransactionCount: 12, grossProfitThisMonth: 4250000 },
  LOGISTIK: { lowStockCount: 1, outOfStockCount: 1, pendingRestockCount: 0 },
  ADMIN: { totalUsers: 4, totalMembers: 2, todayAuditCount: 4 },
}

export const dashboardApi = {
  async summary(role: string): Promise<DashboardSummary> {
    if (MOCK) return mockSummary[role] ?? {}
    const res = await api.get<{ success: true; message: string; data: DashboardSummary }>('/dashboard/summary')
    return res.data.data
  },
}