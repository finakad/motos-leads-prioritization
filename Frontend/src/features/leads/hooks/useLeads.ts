import { useQuery } from '@tanstack/react-query'
import { leadsService } from '../services/leadsService'
import type { LeadsFilter } from '../types/lead'

export const LEADS_QUERY_KEY = 'leads'

export function useLeads(filter?: LeadsFilter) {
  return useQuery({
    queryKey: [LEADS_QUERY_KEY, filter],
    queryFn: () => leadsService.getLeads(filter),
    staleTime: 1000 * 60 * 2, // 2 minutos de frescura
  })
}

export function useLeadDetail(id: string | undefined) {
  return useQuery({
    queryKey: [LEADS_QUERY_KEY, 'detail', id],
    queryFn: () => {
      if (!id) throw new Error('ID de lead no proporcionado')
      return leadsService.getLeadById(id)
    },
    enabled: Boolean(id),
  })
}
