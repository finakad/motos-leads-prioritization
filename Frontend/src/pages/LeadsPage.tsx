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
import { Flame, Info } from 'lucide-react'

const PAGE_SIZE = 10

export function LeadsPage() {
  const { data: rawLeads = [], isLoading, isError, error, refetch } = usePrioritizedLeads()

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
    let result = rawLeads.filter((lead) => {
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

  return (
    <div className="space-y-6">
      {/* Encabezado de pantalla */}
      <header className="space-y-2">
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight flex items-center gap-2.5">
          <Flame className="w-6 h-6 text-amber-500 fill-amber-500/20" aria-hidden="true" />
          Leads priorizados
        </h1>
        <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-900/60 border border-slate-800 px-3 py-1.5 rounded-lg w-fit">
          <Info className="w-3.5 h-3.5 text-amber-400 shrink-0" aria-hidden="true" />
          <span>
            Este listado está usando datos de demostración mientras se integra la API de FastAPI.
          </span>
        </div>
      </header>

      {/* Indicadores / Tarjetas de resumen */}
      <LeadsSummaryCards stats={summaryStats} />

      {/* Filtros locales */}
      <LeadsFilters
        filters={filters}
        onFilterChange={handleFilterChange}
        onClearFilters={handleClearFilters}
        channels={channels}
        statuses={statuses}
        salesPoints={salesPoints}
      />

      {/* Estado: Loading */}
      {isLoading && (
        <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-12">
          <Loader label="Cargando leads priorizados..." />
        </div>
      )}

      {/* Estado: Error */}
      {isError && (
        <ErrorState
          title="Error al consultar leads"
          message={error instanceof Error ? error.message : 'No se pudo obtener el listado de leads.'}
          onRetry={() => refetch()}
        />
      )}

      {/* Estado: Lista vacía */}
      {!isLoading && !isError && totalItems === 0 && (
        <EmptyState
          title="No se encontraron leads coincidentes"
          description="No existen prospectos que cumplan con los filtros seleccionados. Intenta ajustar o limpiar los filtros."
          actionLabel="Limpiar filtros"
          onAction={handleClearFilters}
        />
      )}

      {/* Estado: Datos disponibles */}
      {!isLoading && !isError && totalItems > 0 && (
        <div className="space-y-3">
          <LeadsTable leads={paginatedLeads} />
          <LeadsPagination
            currentPage={currentPage}
            totalPages={totalPages}
            totalItems={totalItems}
            pageSize={PAGE_SIZE}
            onPageChange={setCurrentPage}
          />
        </div>
      )}
    </div>
  )
}
