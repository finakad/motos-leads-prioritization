import type { PrioritizedLead } from './lead.types'
import { MOCK_PRIORITIZED_LEADS } from './leads.mock'

export interface ILeadsService {
  /**
   * Obtiene el listado de leads priorizados.
   * La interfaz está diseñada para poder ser sustituida por llamadas reales
   * a FastAPI sin modificar los componentes de la interfaz.
   */
  getPrioritizedLeads(): Promise<PrioritizedLead[]>
}

class MockLeadsService implements ILeadsService {
  async getPrioritizedLeads(): Promise<PrioritizedLead[]> {
    // Simula una latencia asíncrona breve (300 ms) para verificar estados de carga
    await new Promise((resolve) => setTimeout(resolve, 300))

    // Retorna una copia de los datos mock para evitar mutaciones directas
    return [...MOCK_PRIORITIZED_LEADS]
  }
}

// Exportación del servicio listo para ser sustituido por la integración real con FastAPI
export const leadsService: ILeadsService = new MockLeadsService()
