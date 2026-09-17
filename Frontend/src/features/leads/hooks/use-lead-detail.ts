import { useQuery } from '@tanstack/react-query'
import { leadsService } from '../leads.service'
import type { LeadDetail } from '../lead.types'

export function useLeadDetail(leadId: string | undefined) {
  return useQuery<LeadDetail | null, Error>({
    queryKey: ['lead-detail', leadId],
    queryFn: () => {
      if (!leadId) {
        return Promise.resolve(null)
      }
      return leadsService.getLeadById(leadId)
    },
    enabled: Boolean(leadId),
  })
}
