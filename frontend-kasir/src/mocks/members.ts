import type { MemberLookupResult } from '../types/member'

const members: MemberLookupResult[] = [
  { id: '66f7a1000000000000000020', memberNumber: 'KOP-001', name: 'Budi Santoso' },
  { id: '66f7a1000000000000000021', memberNumber: 'KOP-002', name: 'Siti Aminah' },
]

// Meniru GET /members/lookup/{memberNumber}
export function mockLookupMember(memberNumber: string): Promise<MemberLookupResult> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const found = members.find(
        (m) => m.memberNumber.toLowerCase() === memberNumber.trim().toLowerCase(),
      )
      if (found) resolve(found)
      else reject(new Error('Anggota tidak ditemukan'))
    }, 400) // jeda kecil supaya terasa seperti request sungguhan
  })
}