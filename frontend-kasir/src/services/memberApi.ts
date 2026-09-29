import type { MemberLookupResult } from '../types/member'
import { mockLookupMember } from '../mocks/members'
// import { api } from './api'

export const memberApi = {
  lookup: (memberNumber: string): Promise<MemberLookupResult> => {
    return mockLookupMember(memberNumber)
    // nanti: return api.get<{ data: MemberLookupResult }>(`/members/lookup/${memberNumber}`).then((r) => r.data.data)
  },
}