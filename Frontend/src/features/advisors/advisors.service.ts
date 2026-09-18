import { env } from '@/config/env'
import { apiClient } from '@/services/apiClient'
import type { Advisor } from './advisor.types'
import { MOCK_ADVISORS } from './advisors.mock'
import { AdvisorsListResponseApiSchema } from './advisors.schemas'
import { adaptApiAdvisor } from './advisors.adapters'

export interface IAdvisorsService {
  /**
   * Obtiene el listado de asesores comerciales para una compañía específica.
   */
  getAdvisors(companyId?: string): Promise<Advisor[]>
}

/**
 * Servicio real que consume el endpoint de asesores en FastAPI.
 */
export class ApiAdvisorsService implements IAdvisorsService {
  async getAdvisors(companyId: string = env.defaultCompanyId): Promise<Advisor[]> {
    const raw = await apiClient.get<unknown>(
      `/api/v1/companies/${companyId}/advisors`,
      { companyId }
    )
    const validated = AdvisorsListResponseApiSchema.parse(raw)
    return validated.map(adaptApiAdvisor)
  }
}

/**
 * Servicio mock local como fallback de desarrollo.
 */
export class MockAdvisorsService implements IAdvisorsService {
  async getAdvisors(companyId: string = env.defaultCompanyId): Promise<Advisor[]> {
    await new Promise((resolve) => setTimeout(resolve, 200))
    return MOCK_ADVISORS.filter((a) => !companyId || a.companyId === companyId)
  }
}

export const advisorsService: IAdvisorsService =
  env.dataSource === 'mock' ? new MockAdvisorsService() : new ApiAdvisorsService()
