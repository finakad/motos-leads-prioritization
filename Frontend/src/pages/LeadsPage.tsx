import { useState, useMemo } from 'react'
import { usePrioritizedLeads } from '@/features/leads/hooks/use-prioritized-leads'
import type { LeadsFilterParams, PrioritizedLead } from '@/features/leads/lead.types'
import { LeadsSummaryCards } from '@/features/leads/components/LeadsSummaryCards'
import { LeadsFilters } from '@/features/leads/components/LeadsFilters'
import { LeadsTable } from '@/features/leads/components/LeadsTable'
import { LeadsPagination } from '@/features/leads/components/LeadsPagination'
import { Loader } from '@/components/ui/Loader'
import { ErrorState } from '@/components/ui/ErrorState'
import { EmptyState } from '@/components/ui/EmptyState'
import { Flame, CheckCircle2, Database } from 'lucide-react'
import { env } from '@/config/env'

const PAGE_SIZE = 10
const DEMO_COMPANIES = ['EMP-01', 'EMP-02', 'EMP-03'] as const

export function LeadsPage() {
  const [selectedCompany, setSelectedCompany] = useState<string>(env.defaultCompanyId)
  const {
    data: rawLeads = [],
    isLoading,
    isError,
    error,
    refetch,
  } = usePrioritizedLeads(selectedCompany)

  // Estado de filtros locales
  const [filters, setFilters] = useState<LeadsFilterParams>({
    search: '',
    priority: 'all',
    channel: 'all',
    managementStatus: 'all',
    salesPointId: 'all',
  })

  // Estado de paginación local
  const [currentPage, setCurrentPage] = useState(1)

  // Extraer listas dinámicas únicas para los selectores de filtro
  const { channels, statuses, salesPoints } = useMemo(() => {
    const chSet = new Set<string>()
    const stSet = new Set<string>()
    const spSet = new Set<string>()

    rawLeads.forEach((lead) => {
      if (lead.channel) chSet.add(lead.channel)
      if (lead.managementStatus) stSet.add(lead.managementStatus)
      if (lead.salesPointId) spSet.add(lead.salesPointId)
    })

    return {
      channels: Array.from(chSet).sort(),
      statuses: Array.from(stSet).sort(),
      salesPoints: Array.from(spSet).sort(),
    }
  }, [rawLeads])

  // Filtrado y ordenamiento en memoria
  const filteredAndSortedLeads = useMemo(() => {
    const result = rawLeads.filter((lead) => {
      // Búsqueda por nombre o ID del lead
      if (filters.search && filters.search.trim().length > 0) {
        const query = filters.search.toLowerCase().trim()
        const matchesName = lead.customerName.toLowerCase().includes(query)
        const matchesId = lead.id.toLowerCase().includes(query)
        if (!matchesName && !matchesId) return false
      }

      // Filtro por prioridad
      if (filters.priority && filters.priority !== 'all') {
        if (lead.priority !== filters.priority) return false
      }

      // Filtro por canal
      if (filters.channel && filters.channel !== 'all') {
        if (lead.channel !== filters.channel) return false
      }

      // Filtro por estado de gestión
      if (filters.managementStatus && filters.managementStatus !== 'all') {
        if (lead.managementStatus !== filters.managementStatus) return false
      }

      // Filtro por punto de venta
      if (filters.salesPointId && filters.salesPointId !== 'all') {
        if (lead.salesPointId !== filters.salesPointId) return false
      }

      return true
    })

    // Orden inicial: prioridad alta primero; después score descendente; finalmente fecha descendente
    const priorityWeight: Record<string, number> = {
      high: 3,
      medium: 2,
      low: 1,
    }

    result.sort((a: PrioritizedLead, b: PrioritizedLead) => {
      const priorityDiff = priorityWeight[b.priority] - priorityWeight[a.priority]
      if (priorityDiff !== 0) return priorityDiff

      const scoreA = a.score ?? -Infinity
      const scoreB = b.score ?? -Infinity
      const scoreDiff = scoreB - scoreA
      if (scoreDiff !== 0) return scoreDiff

      const dateA = a.registeredAt ? new Date(a.registeredAt).getTime() : 0
      const dateB = b.registeredAt ? new Date(b.registeredAt).getTime() : 0
      return dateB - dateA
    })

    return result
  }, [rawLeads, filters])

  // Cálculo de resumen con base en los leads visibles filtrados
  const summaryStats = useMemo(() => {
    return {
      total: filteredAndSortedLeads.length,
      high: filteredAndSortedLeads.filter((l) => l.priority === 'high').length,
      medium: filteredAndSortedLeads.filter((l) => l.priority === 'medium').length,
      low: filteredAndSortedLeads.filter((l) => l.priority === 'low').length,
    }
  }, [filteredAndSortedLeads])

  // Paginación local
  const totalItems = filteredAndSortedLeads.length
  const totalPages = Math.ceil(totalItems / PAGE_SIZE)
  const paginatedLeads = useMemo(() => {
    const startIndex = (currentPage - 1) * PAGE_SIZE
    return filteredAndSortedLeads.slice(startIndex, startIndex + PAGE_SIZE)
  }, [filteredAndSortedLeads, currentPage])

  // Manejadores con reinicio a página 1
  const handleFilterChange = (newFilters: LeadsFilterParams) => {
    setFilters(newFilters)
    setCurrentPage(1)
  }

  const handleClearFilters = () => {
    setFilters({
      search: '',
      priority: 'all',
      channel: 'all',
      managementStatus: 'all',
      salesPointId: 'all',
    })
    setCurrentPage(1)
  }

  const handleCompanyChange = (company: string) => {
    setSelectedCompany(company)
    handleClearFilters()
  }

  return (
    <div className="space-y-6">
      {/* Encabezado de pantalla con indicador de origen de datos */}
      <header className="space-y-3">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-100 tracking-tight flex items-center gap-2.5">
              <Flame className="w-6 h-6 text-amber-500 fill-amber-500/20" aria-hidden="true" />
              Leads priorizados
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Consulta operativa de prospectos calificados por probabilidad de conversión.
            </p>
          </div>

          {/* Selector de empresa para verificación de aislamiento multitenant */}
          <div className="flex items-center gap-2 bg-slate-900/80 border border-slate-800 p-1.5 rounded-lg">
            <Database className="w-4 h-4 text-slate-400 ml-1.5" aria-hidden="true" />
            <label htmlFor="company-selector" className="text-xs font-medium text-slate-300">
              Empresa:
            </label>
            <select
              id="company-selector"
              value={selectedCompany}
              onChange={(e) => handleCompanyChange(e.target.value)}
              className="bg-slate-950 text-slate-200 text-xs border border-slate-700 rounded px-2 py-1 font-mono focus:outline-none focus:ring-1 focus:ring-amber-500"
            >
              {DEMO_COMPANIES.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Banner de estado de cartera */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs bg-slate-900/60 border border-slate-800/80 text-slate-300 px-3.5 py-2 rounded-lg">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" aria-hidden="true" />
            <span>
              Cartera sincronizada con el motor de scoring · Sede comercial <strong className="text-slate-100">{selectedCompany}</strong>.
            </span>
          </div>
          <span className="text-[11px] text-emerald-400/90 bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-800/30 shrink-0">
            En tiempo real
          </span>
        </div>
      </header>

      {/* Indicadores / Tarjetas de resumen */}
      <LeadsSummaryCards stats={summaryStats} />

      {/* Filtros locales */}
      <LeadsFilters
        filters={filters}
        channels={channels}
        statuses={statuses}
        salesPoints={salesPoints}
        onFilterChange={handleFilterChange}
        onClearFilters={handleClearFilters}
      />

      {/* Contenido principal según estado de consulta */}
      {isLoading ? (
        <div className="py-20">
          <Loader label={`Cargando prospectos priorizados de ${selectedCompany}...`} />
        </div>
      ) : isError ? (
        <ErrorState
          title="Error al consultar los leads de la empresa"
          message={error instanceof Error ? error.message : 'Error inesperado al conectar con el backend.'}
          onRetry={() => refetch()}
        />
      ) : filteredAndSortedLeads.length === 0 ? (
        <EmptyState
          title="No se encontraron prospectos"
          description={
            rawLeads.length === 0
              ? `No existen registros de leads para la empresa ${selectedCompany} en el backend.`
              : 'No hay prospectos que coincidan con los filtros seleccionados. Intenta restablecer los filtros.'
          }
          actionLabel={rawLeads.length > 0 ? 'Limpiar filtros' : 'Reintentar consulta'}
          onAction={rawLeads.length > 0 ? handleClearFilters : () => refetch()}
        />
      ) : (
        <div className="space-y-4">
          <div className="text-xs text-slate-400 font-medium px-1 flex items-center justify-between">
            <span>
              Mostrando <strong className="text-slate-200">{filteredAndSortedLeads.length}</strong> prospectos filtrados
            </span>
            <span className="text-[11px] text-slate-400">
              Página {currentPage} de {Math.max(1, totalPages)}
            </span>
          </div>

          <LeadsTable leads={paginatedLeads} />

          <LeadsPagination
            currentPage={currentPage}
            totalPages={totalPages}
            totalItems={totalItems}
            pageSize={PAGE_SIZE}
            onPageChange={(page) => setCurrentPage(page)}
          />
        </div>
      )}
    </div>
  )
}
