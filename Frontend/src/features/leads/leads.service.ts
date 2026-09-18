import { env } from '@/config/env'
import { apiClient, ApiNotFoundError } from '@/services/apiClient'
import type { LeadDetail, PrioritizedLead } from './lead.types'
import { MOCK_PRIORITIZED_LEADS } from './leads.mock'
import {
  LeadDetailResponseApiSchema,
  LeadScoreDetailApiSchema,
  LeadConversationsResponseApiSchema,
  PaginatedLeadsResponseApiSchema,
} from './leads.schemas'
import { adaptApiLeadDetail, adaptApiLeadToPrioritizedLead } from './leads.adapters'

export interface ILeadsService {
  /**
   * Obtiene el listado de leads priorizados para una empresa específica.
   */
  getPrioritizedLeads(companyId?: string): Promise<PrioritizedLead[]>

  /**
   * Obtiene el detalle de un lead por identificador, enriquecido con score y conversaciones reales.
   * Devuelve null controlado si el lead no existe en el backend o en el mock.
   */
  getLeadById(leadId: string, companyId?: string): Promise<LeadDetail | null>
}

/**
 * Servicio real que consume la API REST de FastAPI con validación Zod y adaptación de contratos.
 */
export class ApiLeadsService implements ILeadsService {
  async getPrioritizedLeads(companyId: string = env.defaultCompanyId): Promise<PrioritizedLead[]> {
    // Consulta la primera página con tamaño 100 para visualización completa en frontend
    const raw = await apiClient.get<unknown>(
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

    const validated = PaginatedLeadsResponseApiSchema.parse(raw)
    return validated.items.map(adaptApiLeadToPrioritizedLead)
  }

  async getLeadById(
    leadId: string,
    companyId: string = env.defaultCompanyId
  ): Promise<LeadDetail | null> {
    let detailRaw: unknown
    try {
      detailRaw = await apiClient.get<unknown>(
        `/api/v1/companies/${companyId}/leads/${leadId}`,
        { companyId }
      )
    } catch (err) {
      if (err instanceof ApiNotFoundError) {
        return null
      }
      throw err
    }

    const validatedDetail = LeadDetailResponseApiSchema.parse(detailRaw)

    // Consultas complementarias en paralelo para enriquecer la vista operativa
    const [scoreResult, conversationsResult] = await Promise.allSettled([
      apiClient.get<unknown>(
        `/api/v1/companies/${companyId}/leads/${leadId}/score`,
        { companyId }
      ),
      apiClient.get<unknown>(
        `/api/v1/companies/${companyId}/leads/${leadId}/conversations`,
        { companyId }
      ),
    ])

    let validatedScore = null
    if (scoreResult.status === 'fulfilled') {
      try {
        validatedScore = LeadScoreDetailApiSchema.parse(scoreResult.value)
      } catch (validationErr) {
        console.warn('Fallo al validar score contra esquema Zod:', validationErr)
      }
    }

    let validatedConversations = null
    if (conversationsResult.status === 'fulfilled') {
      try {
        validatedConversations = LeadConversationsResponseApiSchema.parse(
          conversationsResult.value
        )
      } catch (validationErr) {
        console.warn('Fallo al validar conversaciones contra esquema Zod:', validationErr)
      }
    }

    return adaptApiLeadDetail(validatedDetail, validatedScore, validatedConversations)
  }
}

/**
 * Servicio mock local conservado como fallback para desarrollo offline o pruebas aisladas.
 */
export class MockLeadsService implements ILeadsService {
  async getPrioritizedLeads(companyId: string = env.defaultCompanyId): Promise<PrioritizedLead[]> {
    await new Promise((resolve) => setTimeout(resolve, 200))
    // Si se especifica una empresa, opcionalmente filtramos o devolvemos los mocks de esa empresa
    return MOCK_PRIORITIZED_LEADS.filter((l) => !companyId || l.companyId === companyId)
  }

  async getLeadById(
    leadId: string,
    _companyId: string = env.defaultCompanyId
  ): Promise<LeadDetail | null> {
    await new Promise((resolve) => setTimeout(resolve, 200))
    const lead = MOCK_PRIORITIZED_LEADS.find((item) => item.id === leadId)
    return lead ? { ...lead } : null
  }
}

/**
 * Instancia activa seleccionada de forma determinista según VITE_DATA_SOURCE ('api' | 'mock')
 */
export const leadsService: ILeadsService =
  env.dataSource === 'mock' ? new MockLeadsService() : new ApiLeadsService()
