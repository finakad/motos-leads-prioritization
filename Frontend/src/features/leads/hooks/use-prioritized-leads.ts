import { useQuery } from '@tanstack/react-query'
import { leadsService } from '../leads.service'
import type { PrioritizedLead } from '../lead.types'
import { env } from '@/config/env'

export function usePrioritizedLeads(companyId: string = env.defaultCompanyId) {
  return useQuery<PrioritizedLead[], Error>({
    queryKey: ['prioritized-leads', companyId],
    queryFn: () => leadsService.getPrioritizedLeads(companyId),
    staleTime: 1000 * 60 * 2, // 2 minutos de caché local
  })
}
