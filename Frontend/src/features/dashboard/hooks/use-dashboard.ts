import { useQuery } from '@tanstack/react-query'
import { dashboardService } from '../dashboard.service'
import type { DashboardData } from '../dashboard.types'
import { env } from '@/config/env'

export function useDashboard(companyId: string = env.defaultCompanyId) {
  return useQuery<DashboardData, Error>({
    queryKey: ['dashboard', companyId, env.dataSource],
    queryFn: () => dashboardService.getDashboardData(companyId),
    staleTime: 1000 * 60 * 2, // 2 minutos de caché
  })
}
