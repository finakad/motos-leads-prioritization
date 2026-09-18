import { env } from '@/config/env'
import { apiClient } from '@/services/apiClient'
import type { CatalogFiltersState, CatalogListResult, Motorcycle } from './catalog.types'
import { MotorcycleListResponseApiSchema, MotorcycleApiSchema } from './catalog.schemas'
import { adaptApiCatalogList, adaptApiMotorcycle } from './catalog.adapters'
import { MOCK_MOTORCYCLES } from './catalog.mock'

export interface ICatalogService {
  getMotorcycles(
    companyId?: string,
    filters?: Partial<CatalogFiltersState>
  ): Promise<CatalogListResult>

  getMotorcycleBySku(sku: string, companyId?: string): Promise<Motorcycle | null>
}

export class ApiCatalogService implements ICatalogService {
  async getMotorcycles(
    companyId: string = env.defaultCompanyId,
    filters?: Partial<CatalogFiltersState>
  ): Promise<CatalogListResult> {
    const params: Record<string, string | number | boolean | null | undefined> = {}

    if (filters?.brand && filters.brand !== 'all') {
      params.brand = filters.brand
    }
    if (filters?.segment && filters.segment !== 'all') {
      params.segment = filters.segment
    }
    if (filters?.salesPointId && filters.salesPointId !== 'all') {
      params.sales_point_id = filters.salesPointId
    }
    if (filters?.search && filters.search.trim()) {
      params.search = filters.search.trim()
    }

    const raw = await apiClient.get<unknown>(
      `/api/v1/companies/${companyId}/catalog/motorcycles`,
      {
        params,
        companyId,
      }
    )

    const validated = MotorcycleListResponseApiSchema.parse(raw)
    return adaptApiCatalogList(validated)
  }

  async getMotorcycleBySku(
    sku: string,
    companyId: string = env.defaultCompanyId
  ): Promise<Motorcycle | null> {
    try {
      const raw = await apiClient.get<unknown>(
        `/api/v1/companies/${companyId}/catalog/motorcycles/${sku}`,
        { companyId }
      )
      const validated = MotorcycleApiSchema.parse(raw)
      return adaptApiMotorcycle(validated)
    } catch (err) {
      console.warn(`Error al consultar detalle del modelo con SKU ${sku}:`, err)
      return null
    }
  }
}

export class MockCatalogService implements ICatalogService {
  async getMotorcycles(
    _companyId: string = env.defaultCompanyId,
    filters?: Partial<CatalogFiltersState>
  ): Promise<CatalogListResult> {
    await new Promise((resolve) => setTimeout(resolve, 200))

    let filtered = [...MOCK_MOTORCYCLES]

    if (filters?.brand && filters.brand !== 'all') {
      filtered = filtered.filter((m) => m.brand.toLowerCase() === filters.brand!.toLowerCase())
    }

    if (filters?.segment && filters.segment !== 'all') {
      filtered = filtered.filter((m) => m.segment.toLowerCase() === filters.segment!.toLowerCase())
    }

    if (filters?.salesPointId && filters.salesPointId !== 'all') {
      filtered = filtered.filter((m) => m.availableSalesPoints.includes(filters.salesPointId!))
    }

    if (filters?.search && filters.search.trim()) {
      const s = filters.search.toLowerCase()
      filtered = filtered.filter(
        (m) =>
          m.line.toLowerCase().includes(s) ||
          m.brand.toLowerCase().includes(s) ||
          m.sku.toLowerCase().includes(s)
      )
    }

    const brands = Array.from(new Set(MOCK_MOTORCYCLES.map((m) => m.brand))).sort()
    const segments = Array.from(new Set(MOCK_MOTORCYCLES.map((m) => m.segment))).sort()

    return {
      items: filtered,
      total: filtered.length,
      brands,
      segments,
    }
  }

  async getMotorcycleBySku(
    sku: string,
    _companyId: string = env.defaultCompanyId
  ): Promise<Motorcycle | null> {
    await new Promise((resolve) => setTimeout(resolve, 150))
    const item = MOCK_MOTORCYCLES.find((m) => m.sku.toLowerCase() === sku.toLowerCase())
    return item ? { ...item } : null
  }
}

export const catalogService: ICatalogService =
  env.dataSource === 'mock' ? new MockCatalogService() : new ApiCatalogService()
