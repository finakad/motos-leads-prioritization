import { env } from '@/config/env'
import { apiClient } from '@/services/http/client'
import { MOCK_LEADS } from '@/services/mocks/leadsMock'
import type { Lead, LeadsFilter, LeadsListResponse } from '../types/lead'

export interface ILeadsService {
  getLeads(filter?: LeadsFilter): Promise<LeadsListResponse>
  getLeadById(id: string): Promise<Lead>
}

// Implementación Mock basada en simulación desacoplada
class MockLeadsService implements ILeadsService {
  async getLeads(filter?: LeadsFilter): Promise<LeadsListResponse> {
    // Simulación de latencia de red para validar estados de loading
    await new Promise((resolve) => setTimeout(resolve, 350))

    // Filtro por tenant / empresa (aislamiento en frontend, refrendado por backend)
    let filtered = MOCK_LEADS.filter((l) => l.companyId === env.companyId)

    if (filter?.search) {
      const q = filter.search.toLowerCase()
      filtered = filtered.filter(
        (l) =>
          l.fullName.toLowerCase().includes(q) ||
          l.modelOfInterest.toLowerCase().includes(q) ||
          l.phone.includes(q)
      )
    }

    if (filter?.priority && filter.priority !== 'TODAS') {
      filtered = filtered.filter((l) => l.priority === filter.priority)
    }

    if (filter?.status && filter.status !== 'TODOS') {
      filtered = filtered.filter((l) => l.status === filter.status)
    }

    if (filter?.channel && filter.channel !== 'TODOS') {
      filtered = filtered.filter((l) => l.channel === filter.channel)
    }

    // Ordenar de mayor a menor score por defecto
    filtered.sort((a, b) => b.score - a.score)

    return {
      data: filtered,
      total: filtered.length,
      companyId: env.companyId,
    }
  }

  async getLeadById(id: string): Promise<Lead> {
    await new Promise((resolve) => setTimeout(resolve, 200))
    const lead = MOCK_LEADS.find(
      (l) => l.id === id && l.companyId === env.companyId
    )
    if (!lead) {
      throw new Error(`Lead con id "${id}" no encontrado en la empresa actual.`)
    }
    return lead
  }
}

// Implementación HTTP conectada (para cuando FastAPI defina el contrato oficial)
class HttpLeadsService implements ILeadsService {
  async getLeads(filter?: LeadsFilter): Promise<LeadsListResponse> {
    return apiClient<LeadsListResponse>('/leads', {
      params: {
        search: filter?.search,
        priority: filter?.priority !== 'TODAS' ? filter?.priority : undefined,
        status: filter?.status !== 'TODOS' ? filter?.status : undefined,
        channel: filter?.channel !== 'TODOS' ? filter?.channel : undefined,
      },
    })
  }

  async getLeadById(id: string): Promise<Lead> {
    return apiClient<Lead>(`/leads/${id}`)
  }
}

// Selector automático según configuración de entorno
export const leadsService: ILeadsService = env.useMocks
  ? new MockLeadsService()
  : new HttpLeadsService()
