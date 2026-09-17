import { useState, useMemo } from 'react'
import {
  useAdvisors,
  enrichAdvisorsWithWorkload,
  filterAndSortAdvisors,
  computeSalesPointSummaries,
  computeAdvisorsGeneralStats,
  getFilterOptions,
  AdvisorsSummaryCards,
  AdvisorsFilters,
  AdvisorsTable,
  SalesPointSummaryTable,
} from '@/features/advisors'
import type { AdvisorsFilterParams } from '@/features/advisors'
import { usePrioritizedLeads } from '@/features/leads'
import { Loader } from '@/components/ui/Loader'
import { ErrorState } from '@/components/ui/ErrorState'
import { EmptyState } from '@/components/ui/EmptyState'
import { Users, Info } from 'lucide-react'

export function AdvisorsPage() {
  const {
    data: rawAdvisors = [],
    isLoading: isLoadingAdvisors,
    isError: isErrorAdvisors,
    error: errorAdvisors,
    refetch: refetchAdvisors,
  } = useAdvisors()

  const {
    data: rawLeads = [],
    isLoading: isLoadingLeads,
    isError: isErrorLeads,
    error: errorLeads,
    refetch: refetchLeads,
  } = usePrioritizedLeads()

  // Estado de filtros locales
  const [filters, setFilters] = useState<AdvisorsFilterParams>({
    search: '',
    companyId: 'all',
    salesPointId: 'all',
    status: 'all',
  })

  // Opciones dinámicas para los selectores de filtro
  const { companies, salesPoints } = useMemo(() => {
    return getFilterOptions(rawAdvisors, filters.companyId)
  }, [rawAdvisors, filters.companyId])

  // Enriquecer asesores con métricas de carga agregadas por punto de venta
  const enrichedAdvisors = useMemo(() => {
    return enrichAdvisorsWithWorkload(rawAdvisors, rawLeads)
  }, [rawAdvisors, rawLeads])

  // Filtrar y ordenar asesores (empresa, punto de venta y nombre)
  const filteredAdvisors = useMemo(() => {
    return filterAndSortAdvisors(enrichedAdvisors, filters)
  }, [enrichedAdvisors, filters])

  // Calcular los 6 indicadores generales para los asesores visibles
  const generalStats = useMemo(() => {
    return computeAdvisorsGeneralStats(filteredAdvisors, rawLeads)
  }, [filteredAdvisors, rawLeads])

  // Calcular el resumen ordenado por punto de venta
  const salesPointSummaries = useMemo(() => {
    return computeSalesPointSummaries(rawAdvisors, rawLeads, filters)
  }, [rawAdvisors, rawLeads, filters])

  const isLoading = isLoadingAdvisors || isLoadingLeads
  const isError = isErrorAdvisors || isErrorLeads

  const handleClearFilters = () => {
    setFilters({
      search: '',
      companyId: 'all',
      salesPointId: 'all',
      status: 'all',
    })
  }

  const handleRetryAll = () => {
    refetchAdvisors()
    refetchLeads()
  }

  return (
    <div className="space-y-6">
      {/* 1. Encabezado */}
      <header className="space-y-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight flex items-center gap-2.5">
            <Users className="w-6 h-6 text-emerald-400" aria-hidden="true" />
            Asesores y capacidad operativa
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Vista de demostración basada en datos mock locales.
          </p>
        </div>

        {/* Aviso visible de métricas agregadas */}
        <div className="flex items-start gap-2.5 p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-300">
          <Info className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" aria-hidden="true" />
          <span>
            Las cargas se calculan de forma agregada por punto de venta y no representan asignaciones reales.
          </span>
        </div>
      </header>

      {/* 2. Filtros locales */}
      <AdvisorsFilters
        filters={filters}
        onFilterChange={setFilters}
        onClearFilters={handleClearFilters}
        companies={companies}
        salesPoints={salesPoints}
      />

      {/* Estado: Carga */}
      {isLoading && (
        <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-12">
          <Loader label="Calculando capacidad comercial y agregaciones de sede..." />
        </div>
      )}

      {/* Estado: Error */}
      {isError && (
        <ErrorState
          title="Error al cargar capacidad operativa"
          message={
            errorAdvisors instanceof Error
              ? errorAdvisors.message
              : errorLeads instanceof Error
                ? errorLeads.message
                : 'No se pudo cargar la información de asesores y puntos de venta.'
          }
          onRetry={handleRetryAll}
        />
      )}

      {/* Estado: Lista vacía tras filtros */}
      {!isLoading && !isError && filteredAdvisors.length === 0 && (
        <EmptyState
          title="No se encontraron asesores coincidentes"
          description="Ningún asesor coincide con los criterios de búsqueda, empresa o punto de venta seleccionados."
          actionLabel="Limpiar filtros"
          onAction={handleClearFilters}
        />
      )}

      {/* Estado: Datos disponibles */}
      {!isLoading && !isError && filteredAdvisors.length > 0 && (
        <div className="space-y-6">
          {/* 3. Indicadores generales */}
          <AdvisorsSummaryCards stats={generalStats} />

          {/* 4. Tabla de asesores */}
          <section aria-labelledby="tabla-asesores-title" className="space-y-3">
            <div className="flex items-center justify-between text-xs text-slate-400 px-1">
              <h2 id="tabla-asesores-title" className="font-semibold text-slate-200 text-sm">
                Detalle operativo por asesor
              </h2>
              <span>
                Mostrando <strong className="text-slate-200">{filteredAdvisors.length}</strong> de{' '}
                <strong className="text-slate-200">{rawAdvisors.length}</strong> asesores
              </span>
            </div>
            <AdvisorsTable advisors={filteredAdvisors} />
          </section>

          {/* 5. Resumen por punto de venta */}
          <section aria-label="Resumen por punto de venta">
            <SalesPointSummaryTable summaries={salesPointSummaries} />
          </section>
        </div>
      )}
    </div>
  )
}
