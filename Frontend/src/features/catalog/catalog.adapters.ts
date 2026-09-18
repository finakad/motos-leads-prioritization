import type { MotorcycleApi, MotorcycleListResponseApi } from './catalog.schemas'
import type { CatalogListResult, CatalogSummaryMetrics, Motorcycle } from './catalog.types'

export function adaptApiMotorcycle(item: MotorcycleApi): Motorcycle {
  return {
    sku: item.sku,
    brand: item.brand,
    line: item.line,
    engineDisplacementCc: item.engine_displacement_cc,
    segment: item.segment,
    listPrice: item.list_price,
    reportedAvailableUnits: item.reported_available_units,
    availableSalesPoints: item.available_sales_points,
  }
}

export function adaptApiCatalogList(apiData: MotorcycleListResponseApi): CatalogListResult {
  return {
    items: apiData.items.map(adaptApiMotorcycle),
    total: apiData.total,
    brands: apiData.brands,
    segments: apiData.segments,
  }
}

export function formatPriceCOP(price: number): string {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0,
  }).format(price)
}

export function computeCatalogMetrics(items: Motorcycle[]): CatalogSummaryMetrics {
  if (items.length === 0) {
    return {
      totalModels: 0,
      activeBrands: 0,
      totalUnits: 0,
      minPrice: 0,
      maxPrice: 0,
      avgPrice: 0,
    }
  }

  const brandsSet = new Set(items.map((m) => m.brand))
  let totalUnits = 0
  let minPrice = items[0].listPrice
  let maxPrice = items[0].listPrice
  let priceSum = 0

  for (const m of items) {
    totalUnits += m.reportedAvailableUnits
    if (m.listPrice < minPrice) minPrice = m.listPrice
    if (m.listPrice > maxPrice) maxPrice = m.listPrice
    priceSum += m.listPrice
  }

  return {
    totalModels: items.length,
    activeBrands: brandsSet.size,
    totalUnits,
    minPrice,
    maxPrice,
    avgPrice: Math.round(priceSum / items.length),
  }
}
