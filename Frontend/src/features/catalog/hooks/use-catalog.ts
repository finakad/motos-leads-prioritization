import { useQuery } from '@tanstack/react-query'
import { catalogService } from '../catalog.service'
import type { CatalogFiltersState, CatalogListResult } from '../catalog.types'
import { env } from '@/config/env'

export function useCatalog(
  companyId: string = env.defaultCompanyId,
  filters?: Partial<CatalogFiltersState>
) {
  return useQuery<CatalogListResult, Error>({
    queryKey: ['catalog', companyId, filters, env.dataSource],
    queryFn: () => catalogService.getMotorcycles(companyId, filters),
    staleTime: 1000 * 60 * 3, // 3 minutos de caché
  })
}
