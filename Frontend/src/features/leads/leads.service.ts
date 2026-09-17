import type { LeadDetail, PrioritizedLead } from './lead.types'
import { MOCK_PRIORITIZED_LEADS } from './leads.mock'

export interface ILeadsService {
  /**
   * Obtiene el listado de leads priorizados.
   * Diseñado para ser sustituido por FastAPI sin alterar los componentes.
   */
  getPrioritizedLeads(): Promise<PrioritizedLead[]>

  /**
   * Obtiene el detalle de un lead por identificador.
   * Devuelve el objeto LeadDetail correspondiente o null controlado cuando no exista.
   */
  getLeadById(leadId: string): Promise<LeadDetail | null>
}

class MockLeadsService implements ILeadsService {
  async getPrioritizedLeads(): Promise<PrioritizedLead[]> {
    // Simula una latencia asíncrona breve (300 ms) para verificar estados de carga
    await new Promise((resolve) => setTimeout(resolve, 300))
    return [...MOCK_PRIORITIZED_LEADS]
  }

  async getLeadById(leadId: string): Promise<LeadDetail | null> {
    // Simula una latencia asíncrona breve (300 ms) para verificar estados de carga
    await new Promise((resolve) => setTimeout(resolve, 300))
    const lead = MOCK_PRIORITIZED_LEADS.find((item) => item.id === leadId)
    return lead ? { ...lead } : null
  }
}

// Exportación del servicio listo para ser sustituido por la integración real con FastAPI
export const leadsService: ILeadsService = new MockLeadsService()
