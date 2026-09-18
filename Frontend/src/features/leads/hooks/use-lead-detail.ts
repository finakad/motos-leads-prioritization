import { useQuery } from '@tanstack/react-query'
import { leadsService } from '../leads.service'
import type { LeadDetail } from '../lead.types'
import { env } from '@/config/env'

export function useLeadDetail(leadId: string | undefined, companyId: string = env.defaultCompanyId) {
  return useQuery<LeadDetail | null, Error>({
    queryKey: ['lead-detail', leadId, companyId],
    queryFn: () => {
      if (!leadId) {
        return Promise.resolve(null)
      }
      return leadsService.getLeadById(leadId, companyId)
    },
    enabled: Boolean(leadId),
  })
}
