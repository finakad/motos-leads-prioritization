import { useQuery } from '@tanstack/react-query'
import { advisorsService } from '../advisors.service'
import type { Advisor } from '../advisor.types'
import { env } from '@/config/env'

export function useAdvisors(companyId: string = env.defaultCompanyId) {
  return useQuery<Advisor[], Error>({
    queryKey: ['advisors', companyId],
    queryFn: () => advisorsService.getAdvisors(companyId),
    staleTime: 1000 * 60 * 2, // 2 minutos de caché local
  })
}
