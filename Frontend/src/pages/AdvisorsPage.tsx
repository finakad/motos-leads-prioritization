import { useState, useMemo } from 'react'
import {
  useAdvisors,
  enrichAdvisorsWithWorkload,
  filterAndSortAdvisors,
  computeSalesPointSummaries,
  computeAdvisorsGeneralStats,
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
import { Users, CheckCircle2, AlertTriangle, Building2, UserCheck } from 'lucide-react'
import { env } from '@/config/env'

const AVAILABLE_COMPANIES = ['EMP-01', 'EMP-02', 'EMP-03']

export function AdvisorsPage() {
  // Filtros locales: inicializar con la empresa activa por defecto
  const [filters, setFilters] = useState<AdvisorsFilterParams>({
    search: '',
    companyId: env.defaultCompanyId,
    salesPointId: 'all',
    status: 'all',
  })

  const currentCompany = filters.companyId && filters.companyId !== 'all'
    ? filters.companyId
    : env.defaultCompanyId

  // Consulta de asesores reales para la empresa seleccionada
  const {
    data: rawAdvisors = [],
    isLoading: isLoadingAdvisors,
    isError: isErrorAdvisors,
    error: errorAdvisors,
    refetch: refetchAdvisors,
  } = useAdvisors(currentCompany)

  // Consulta de leads reales para la misma empresa
  const {
    data: rawLeads = [],
    isLoading: isLoadingLeads,
    isError: isErrorLeads,
    error: errorLeads,
    refetch: refetchLeads,
  } = usePrioritizedLeads(currentCompany)

  // Opciones de puntos de venta según los asesores y leads de la empresa activa
  const salesPoints = useMemo(() => {
    const spSet = new Set<string>()
    rawAdvisors.forEach((a) => spSet.add(a.salesPointId))
    rawLeads.forEach((l) => spSet.add(l.salesPointId))
    return Array.from(spSet).sort()
  }, [rawAdvisors, rawLeads])

  // Enriquecer asesores con métricas de capacidad
  const enrichedAdvisors = useMemo(() => {
    return enrichAdvisorsWithWorkload(rawAdvisors, rawLeads)
  }, [rawAdvisors, rawLeads])

  // Filtrar y ordenar asesores
  const filteredAdvisors = useMemo(() => {
    return filterAndSortAdvisors(enrichedAdvisors, filters)
  }, [enrichedAdvisors, filters])

  // Calcular los 6 indicadores generales
  const generalStats = useMemo(() => {
    return computeAdvisorsGeneralStats(filteredAdvisors, rawLeads)
  }, [filteredAdvisors, rawLeads])

  // Calcular el resumen por punto de venta (ordenado por leads de alta prioridad)
  const salesPointSummaries = useMemo(() => {
    return computeSalesPointSummaries(rawAdvisors, rawLeads, filters)
  }, [rawAdvisors, rawLeads, filters])

  const isLoading = isLoadingAdvisors || isLoadingLeads
  const isError = isErrorAdvisors || isErrorLeads

  const handleFilterChange = (newFilters: AdvisorsFilterParams) => {
    setFilters(newFilters)
  }

  const handleClearFilters = () => {
    setFilters({
      search: '',
      companyId: currentCompany,
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
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-100 tracking-tight flex items-center gap-2.5">
              <Users className="w-6 h-6 text-emerald-400" aria-hidden="true" />
              Capacidad comercial y asesores por sede
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Monitoreo operativo de carga, demanda de leads calificados y capacidad instalada por punto de venta.
            </p>
          </div>

          <div className="flex items-center gap-2 bg-slate-900/80 border border-slate-800 px-3 py-1.5 rounded-lg text-xs font-mono text-slate-300 self-start md:self-auto">
            <Building2 className="w-4 h-4 text-amber-400" aria-hidden="true" />
            <span>Empresa activa: <strong className="text-slate-100">{currentCompany}</strong></span>
          </div>
        </div>

        {/* Banner de estado de integración con FastAPI */}
        {env.dataSource === 'api' ? (
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs bg-emerald-950/30 border border-emerald-800/50 text-emerald-300 px-3.5 py-2 rounded-lg">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" aria-hidden="true" />
              <span>
                Conectado a <strong>FastAPI local</strong> (<code>/companies/{currentCompany}/advisors</code>). Nómina y capacidad sincronizada en tiempo real con PostgreSQL.
              </span>
            </div>
            <span className="text-[11px] text-emerald-400/80 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800/40 shrink-0">
              Datos reales
            </span>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-xs text-amber-300 bg-amber-950/30 border border-amber-800/50 px-3.5 py-2 rounded-lg">
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" aria-hidden="true" />
            <span>Modo de demostración activo con datos mock locales.</span>
          </div>
        )}
      </header>

      {/* 2. Filtros */}
      <AdvisorsFilters
        filters={filters}
        onFilterChange={handleFilterChange}
        onClearFilters={handleClearFilters}
        companies={AVAILABLE_COMPANIES}
        salesPoints={salesPoints}
      />

      {/* Estado: Carga */}
      {isLoading && (
        <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-12">
          <Loader label={`Consultando asesores y carga de ${currentCompany} desde FastAPI...`} />
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
                : 'No se pudo consultar la información de asesores en el servidor backend.'
          }
          onRetry={handleRetryAll}
        />
      )}

      {/* Estado: Lista vacía tras filtros */}
      {!isLoading && !isError && filteredAdvisors.length === 0 && (
        <EmptyState
          title="No se encontraron asesores coincidentes"
          description="Ningún asesor coincide con los criterios de búsqueda o punto de venta seleccionados."
          actionLabel="Limpiar filtros"
          onAction={handleClearFilters}
        />
      )}

      {/* Estado: Datos disponibles */}
      {!isLoading && !isError && filteredAdvisors.length > 0 && (
        <div className="space-y-6">
          {/* 3. Indicadores generales */}
          <AdvisorsSummaryCards stats={generalStats} />

          {/* 4. Nivel 1: Tablero de Capacidad y Saturación por Punto de Venta (Prioridad Operativa) */}
          <section aria-labelledby="resumen-sedes-title" className="space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-xs text-slate-400 px-1">
              <div>
                <h2 id="resumen-sedes-title" className="font-semibold text-slate-100 text-sm flex items-center gap-2">
                  <Building2 className="w-4 h-4 text-cyan-400" aria-hidden="true" />
                  Saturación y Capacidad por Punto de Venta (Sede)
                </h2>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  Identifica cuellos de botella: compara demanda de leads de prioridad ALTA frente a la capacidad diaria de los asesores activos.
                </p>
              </div>
              <span className="text-[11px] text-slate-400">
                Ordenado por criticidad (leads ALTA prioridad)
              </span>
            </div>
            <SalesPointSummaryTable summaries={salesPointSummaries} />
          </section>

          {/* 5. Nivel 2: Nómina y Disponibilidad de Asesores */}
          <section aria-labelledby="tabla-asesores-title" className="space-y-3 pt-2">
            <div className="flex items-center justify-between text-xs text-slate-400 px-1">
              <h2 id="tabla-asesores-title" className="font-semibold text-slate-100 text-sm flex items-center gap-2">
                <UserCheck className="w-4 h-4 text-emerald-400" aria-hidden="true" />
                Nómina Operativa de Asesores
              </h2>
              <span>
                Mostrando <strong className="text-slate-200">{filteredAdvisors.length}</strong> de{' '}
                <strong className="text-slate-200">{rawAdvisors.length}</strong> asesores
              </span>
            </div>
            <AdvisorsTable advisors={filteredAdvisors} />
          </section>
        </div>
      )}
    </div>
  )
}
