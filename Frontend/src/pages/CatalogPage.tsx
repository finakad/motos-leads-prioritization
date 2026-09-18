import { useState, useMemo } from 'react'
import {
  useCatalog,
  CatalogHeader,
  CatalogSummaryCards,
  CatalogFilters,
  CatalogGrid,
  MotorcycleDetailModal,
  computeCatalogMetrics,
  type CatalogFiltersState,
  type Motorcycle,
} from '@/features/catalog'
import { Loader } from '@/components/ui/Loader'
import { ErrorState } from '@/components/ui/ErrorState'
import { EmptyState } from '@/components/ui/EmptyState'
import { env } from '@/config/env'

const DEFAULT_FILTERS: CatalogFiltersState = {
  search: '',
  brand: 'all',
  segment: 'all',
  salesPointId: 'all',
  sortBy: 'price-asc',
}

export function CatalogPage() {
  const [selectedCompany, setSelectedCompany] = useState<string>(env.defaultCompanyId)
  const [filters, setFilters] = useState<CatalogFiltersState>(DEFAULT_FILTERS)
  const [selectedMotorcycle, setSelectedMotorcycle] = useState<Motorcycle | null>(null)

  const {
    data,
    isLoading,
    isError,
    error,
    refetch,
    isRefetching,
  } = useCatalog(selectedCompany, {
    brand: filters.brand,
    segment: filters.segment,
    salesPointId: filters.salesPointId,
    search: filters.search,
  })

  // Extraer sedes únicas para el filtro
  const salesPoints = useMemo(() => {
    if (!data?.items) return []
    const spSet = new Set<string>()
    data.items.forEach((m) => {
      m.availableSalesPoints.forEach((sp) => spSet.add(sp))
    })
    return Array.from(spSet).sort()
  }, [data])

  // Ordenamiento en memoria de los modelos
  const sortedMotorcycles = useMemo(() => {
    if (!data?.items) return []
    const items = [...data.items]

    switch (filters.sortBy) {
      case 'price-asc':
        return items.sort((a, b) => a.listPrice - b.listPrice)
      case 'price-desc':
        return items.sort((a, b) => b.listPrice - a.listPrice)
      case 'cc-asc':
        return items.sort((a, b) => a.engineDisplacementCc - b.engineDisplacementCc)
      case 'cc-desc':
        return items.sort((a, b) => b.engineDisplacementCc - a.engineDisplacementCc)
      case 'name':
        return items.sort((a, b) => a.line.localeCompare(b.line))
      default:
        return items
    }
  }, [data, filters.sortBy])

  const metrics = useMemo(() => {
    return computeCatalogMetrics(sortedMotorcycles)
  }, [sortedMotorcycles])

  return (
    <div className="space-y-6">
      {/* Encabezado Principal y Selector de Empresa */}
      <CatalogHeader
        selectedCompany={selectedCompany}
        onSelectCompany={(compId) => {
          setSelectedCompany(compId)
          setFilters(DEFAULT_FILTERS)
        }}
        dataSource={env.dataSource}
        totalModels={data?.total ?? 0}
        onRefresh={() => void refetch()}
        isRefreshing={isRefetching}
      />

      {/* Estados de Carga y Error */}
      {isLoading ? (
        <div className="py-20 flex justify-center">
          <Loader label={`Cargando catálogo de motocicletas para ${selectedCompany}...`} />
        </div>
      ) : isError ? (
        <ErrorState
          title={`Error al cargar el catálogo de ${selectedCompany}`}
          message={
            error?.message ||
            'No fue posible obtener el catálogo desde el servidor.'
          }
          onRetry={() => void refetch()}
        />
      ) : (
        <>
          {/* Tarjetas KPI Superiores */}
          <CatalogSummaryCards metrics={metrics} />

          {/* Filtros de Búsqueda y Ordenamiento */}
          <CatalogFilters
            filters={filters}
            onChange={setFilters}
            brands={data?.brands ?? []}
            segments={data?.segments ?? []}
            salesPoints={salesPoints}
            onReset={() => setFilters(DEFAULT_FILTERS)}
          />

          {/* Cuadrícula de Motocicletas o Estado Vacío */}
          {sortedMotorcycles.length === 0 ? (
            <EmptyState
              title="No se encontraron motocicletas"
              description="No hay modelos que coincidan con los filtros de búsqueda o sede seleccionados."
              actionLabel="Restablecer Filtros"
              onAction={() => setFilters(DEFAULT_FILTERS)}
            />
          ) : (
            <CatalogGrid
              motorcycles={sortedMotorcycles}
              onSelect={(m) => setSelectedMotorcycle(m)}
            />
          )}

          {/* Modal de Ficha Técnica Detallada */}
          <MotorcycleDetailModal
            motorcycle={selectedMotorcycle}
            onClose={() => setSelectedMotorcycle(null)}
          />
        </>
      )}
    </div>
  )
}
