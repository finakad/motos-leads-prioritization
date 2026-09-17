import { useQuery } from '@tanstack/react-query'
import { advisorsService } from '../advisors.service'
import type { Advisor } from '../advisor.types'

export const ADVISORS_QUERY_KEY = ['advisors'] as const

export function useAdvisors() {
  return useQuery<Advisor[], Error>({
    queryKey: ADVISORS_QUERY_KEY,
    queryFn: () => advisorsService.getAdvisors(),
    staleTime: 1000 * 60 * 2,
  })
}
