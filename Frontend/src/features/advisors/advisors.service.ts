import type { Advisor } from './advisor.types'
import { MOCK_ADVISORS } from './advisors.mock'

export interface IAdvisorsService {
  /**
   * Obtiene el listado de asesores comerciales.
   * Diseñado para ser sustituido por FastAPI sin alterar componentes de presentación.
   */
  getAdvisors(): Promise<Advisor[]>
}

class MockAdvisorsService implements IAdvisorsService {
  async getAdvisors(): Promise<Advisor[]> {
    // Simula latencia asíncrona breve (300 ms) para verificar estados de carga
    await new Promise((resolve) => setTimeout(resolve, 300))
    return [...MOCK_ADVISORS]
  }
}

export const advisorsService: IAdvisorsService = new MockAdvisorsService()
