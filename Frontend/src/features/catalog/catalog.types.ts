export interface Motorcycle {
  sku: string
  brand: string
  line: string
  engineDisplacementCc: number
  segment: string
  listPrice: number
  reportedAvailableUnits: number
  availableSalesPoints: string[]
}

export interface CatalogListResult {
  items: Motorcycle[]
  total: number
  brands: string[]
  segments: string[]
}

export interface CatalogFiltersState {
  search: string
  brand: string
  segment: string
  salesPointId: string
  sortBy: 'price-asc' | 'price-desc' | 'cc-asc' | 'cc-desc' | 'name'
}

export interface CatalogSummaryMetrics {
  totalModels: number
  activeBrands: number
  totalUnits: number
  minPrice: number
  maxPrice: number
  avgPrice: number
}
