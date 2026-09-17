import { useState } from 'react'
import { useLeads } from '@/features/leads/hooks/useLeads'
import type { LeadsFilter } from '@/features/leads/types/lead'
import { LeadsFilterBar } from '@/features/leads/components/LeadsFilterBar'
import { LeadsTable } from '@/features/leads/components/LeadsTable'
import { Loader } from '@/components/ui/Loader'
import { EmptyState } from '@/components/ui/EmptyState'
import { ErrorState } from '@/components/ui/ErrorState'
import { Flame, Sparkles, TrendingUp, Users } from 'lucide-react'

export function LeadsPage() {
  const [filter, setFilter] = useState<LeadsFilter>({})

  const { data, isLoading, isError, error, refetch } = useLeads(filter)

  const leads = data?.data || []
  const totalLeads = leads.length
  const highPriorityCount = leads.filter((l) => l.priority === 'ALTA').length
  const avgScore = totalLeads > 0
    ? Math.round(leads.reduce((acc, l) => acc + l.score, 0) / totalLeads)
    : 0

  return (
    <div className="space-y-6">
      {/* Top Banner / Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight flex items-center gap-2.5">
            <Flame className="w-6 h-6 text-amber-500 fill-amber-500/20" />
            Priorización de Leads
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Gestiona prospectos de motocicletas ordenados predictivamente por probabilidad de compra.
          </p>
        </div>

        {/* Quick KPI stats */}
        <div className="grid grid-cols-3 gap-2 sm:gap-3 shrink-0">
          <div className="bg-slate-900/80 border border-slate-800 rounded-lg px-3.5 py-2 text-center">
            <div className="flex items-center justify-center gap-1 text-[11px] font-semibold text-slate-400 uppercase">
              <Users className="w-3 h-3 text-cyan-400" />
              Total
            </div>
            <div className="text-lg font-bold text-slate-100 font-mono mt-0.5">
              {totalLeads}
            </div>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 rounded-lg px-3.5 py-2 text-center">
            <div className="flex items-center justify-center gap-1 text-[11px] font-semibold text-rose-400 uppercase">
              <Flame className="w-3 h-3" />
              Alta
            </div>
            <div className="text-lg font-bold text-rose-400 font-mono mt-0.5">
              {highPriorityCount}
            </div>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 rounded-lg px-3.5 py-2 text-center">
            <div className="flex items-center justify-center gap-1 text-[11px] font-semibold text-amber-400 uppercase">
              <Sparkles className="w-3 h-3" />
              Score Prom.
            </div>
            <div className="text-lg font-bold text-amber-400 font-mono mt-0.5">
              {avgScore}
            </div>
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <LeadsFilterBar
        filter={filter}
        onFilterChange={setFilter}
        onReset={() => setFilter({})}
      />

      {/* Estados de UI: Loading, Error, Empty, Data */}
      {isLoading && (
        <div className="bg-slate-900/40 border border-slate-800/80 rounded-xl p-12">
          <Loader label="Analizando y priorizando prospectos comerciales..." />
        </div>
      )}

      {isError && (
        <ErrorState
          title="Error al consultar leads"
          message={error instanceof Error ? error.message : 'No se pudo obtener el listado de leads.'}
          onRetry={() => refetch()}
        />
      )}

      {!isLoading && !isError && leads.length === 0 && (
        <EmptyState
          title="No se encontraron leads con estos filtros"
          description="Intenta cambiar los parámetros de búsqueda, prioridad o estado para ver más resultados."
          actionLabel="Restablecer Filtros"
          onAction={() => setFilter({})}
        />
      )}

      {!isLoading && !isError && leads.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-400 px-1">
            <span>
              Mostrando <strong className="text-slate-200">{leads.length}</strong> prospectos activos
            </span>
            <span className="flex items-center gap-1 text-slate-400">
              <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
              Ordenados por mayor score predictivo
            </span>
          </div>
          <LeadsTable leads={leads} />
        </div>
      )}
    </div>
  )
}
