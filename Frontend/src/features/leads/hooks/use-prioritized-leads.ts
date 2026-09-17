import { useQuery } from '@tanstack/react-query'
import { leadsService } from '../leads.service'
import type { PrioritizedLead } from '../lead.types'

export const PRIORITIZED_LEADS_QUERY_KEY = ['prioritized-leads'] as const

export function usePrioritizedLeads() {
  return useQuery<PrioritizedLead[], Error>({
    queryKey: PRIORITIZED_LEADS_QUERY_KEY,
    queryFn: () => leadsService.getPrioritizedLeads(),
    staleTime: 1000 * 60 * 2, // 2 minutos de caché local
  })
}
