import { env } from '@/config/env'
import { apiClient } from '@/services/apiClient'
import type { DashboardData } from './dashboard.types'
import { PaginatedLeadsResponseApiSchema, type LeadPrioritizedItemApi } from './dashboard.schemas'
import { adaptApiLeadsToDashboard } from './dashboard.adapters'
import { MOCK_DASHBOARD_DATA } from './dashboard.mock'

export interface IDashboardService {
  /**
   * Obtiene la estructura analítica del dashboard para la empresa especificada.
   * En modo API, realiza la derivación de métricas a partir del censo real de leads priorizados.
   * En modo mock, retorna el set de demostración local.
   */
  getDashboardData(companyId?: string): Promise<DashboardData>
}

/**
 * Servicio real que consume los leads priorizados de FastAPI y deriva las métricas del dashboard.
 * Aplica validación estricta Zod y segregación por empresa.
 */
export class ApiDashboardService implements IDashboardService {
  async getDashboardData(companyId: string = env.defaultCompanyId): Promise<DashboardData> {
    // 1. Obtener primera página (100 registros)
    const firstPageRaw = await apiClient.get<unknown>(
      `/api/v1/companies/${companyId}/leads/prioritized`,
      {
        params: {
          page: 1,
          page_size: 100,
          order_by: 'score',
          order_direction: 'desc',
        },
        companyId,
      }
    )

    const firstPage = PaginatedLeadsResponseApiSchema.parse(firstPageRaw)
    const allItems: LeadPrioritizedItemApi[] = [...firstPage.items]
    const totalCompanyLeads = firstPage.total

    // 2. Si hay páginas adicionales y el total es manejable (<= 600 leads), consultar páginas restantes en paralelo
    const maxPagesToFetch = Math.min(firstPage.total_pages, 6)
    if (maxPagesToFetch > 1) {
      const pagePromises: Promise<unknown>[] = []
      for (let p = 2; p <= maxPagesToFetch; p++) {
        pagePromises.push(
          apiClient.get<unknown>(
            `/api/v1/companies/${companyId}/leads/prioritized`,
            {
              params: {
                page: p,
                page_size: 100,
                order_by: 'score',
                order_direction: 'desc',
              },
              companyId,
            }
          )
        )
      }

      const results = await Promise.all(pagePromises)
      for (const res of results) {
        const validated = PaginatedLeadsResponseApiSchema.parse(res)
        allItems.push(...validated.items)
      }
    }

    return adaptApiLeadsToDashboard(allItems, totalCompanyLeads, companyId, 'api')
  }
}

/**
 * Servicio mock local para desarrollo offline o pruebas de UI.
 */
export class MockDashboardService implements IDashboardService {
  async getDashboardData(companyId: string = env.defaultCompanyId): Promise<DashboardData> {
    await new Promise((resolve) => setTimeout(resolve, 200))
    const mock = MOCK_DASHBOARD_DATA[companyId] ?? MOCK_DASHBOARD_DATA['EMP-01']
    return {
      ...mock,
      metadata: {
        ...mock.metadata,
        companyId,
        syncTime: new Date().toLocaleTimeString('es-CO', {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
        }),
      },
    }
  }
}

export const dashboardService: IDashboardService =
  env.dataSource === 'mock' ? new MockDashboardService() : new ApiDashboardService()
