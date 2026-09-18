import type { AdvisorsFilterParams, AdvisorStatus } from '../advisor.types'
import { Search, X, ShieldAlert } from 'lucide-react'
import { Button } from '@/components/ui/Button'

interface AdvisorsFiltersProps {
  filters: AdvisorsFilterParams
  onFilterChange: (newFilters: AdvisorsFilterParams) => void
  onClearFilters: () => void
  companies: string[]
  salesPoints: string[]
}

export function AdvisorsFilters({
  filters,
  onFilterChange,
  onClearFilters,
  companies,
  salesPoints,
}: AdvisorsFiltersProps) {
  const hasActiveFilters = Boolean(
    (filters.search && filters.search.trim().length > 0) ||
      (filters.companyId && filters.companyId !== 'all') ||
      (filters.salesPointId && filters.salesPointId !== 'all') ||
      (filters.status && filters.status !== 'all')
  )

  const handleCompanyChange = (companyId: string) => {
    // Al cambiar de empresa, restablecer punto de venta si ya no aplica
    onFilterChange({
      ...filters,
      companyId,
      salesPointId: 'all',
    })
  }

  return (
    <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-4">
      {/* Aviso visible de segregación */}
      <div className="flex items-start gap-2 text-xs text-slate-400 bg-slate-950/60 border border-slate-800 px-3 py-2 rounded-lg">
        <ShieldAlert className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" aria-hidden="true" />
        <span>
          Este filtro es solo visual y no sustituye la segregación de datos que debe aplicar FastAPI.
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Búsqueda por nombre o ID */}
        <div>
          <label
            htmlFor="filter-advisor-search"
            className="block text-xs font-medium text-slate-300 mb-1"
          >
            Buscar asesor o ID
          </label>
          <div className="relative">
            <Search
              className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2"
              aria-hidden="true"
            />
            <input
              id="filter-advisor-search"
              type="text"
              placeholder="Ej. Daniela o ADV-001"
              value={filters.search || ''}
              onChange={(e) =>
                onFilterChange({ ...filters, search: e.target.value })
              }
              className="w-full pl-9 pr-3 py-1.5 bg-slate-950/80 border border-slate-700/80 rounded-lg text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
            />
          </div>
        </div>

        {/* Empresa */}
        <div>
          <label
            htmlFor="filter-advisor-company"
            className="block text-xs font-medium text-slate-300 mb-1"
          >
            Empresa
          </label>
          <select
            id="filter-advisor-company"
            value={filters.companyId || ''}
            onChange={(e) => handleCompanyChange(e.target.value)}
            className="w-full px-2.5 py-1.5 bg-slate-950/80 border border-slate-700/80 rounded-lg text-xs text-slate-100 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
          >
            {companies.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        {/* Punto de venta */}
        <div>
          <label
            htmlFor="filter-advisor-sales-point"
            className="block text-xs font-medium text-slate-300 mb-1"
          >
            Punto de venta
          </label>
          <select
            id="filter-advisor-sales-point"
            value={filters.salesPointId || 'all'}
            onChange={(e) =>
              onFilterChange({
                ...filters,
                salesPointId: e.target.value,
              })
            }
            className="w-full px-2.5 py-1.5 bg-slate-950/80 border border-slate-700/80 rounded-lg text-xs text-slate-100 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
          >
            <option value="all">Todos los puntos de venta</option>
            {salesPoints.map((sp) => (
              <option key={sp} value={sp}>
                {sp}
              </option>
            ))}
          </select>
        </div>

        {/* Estado */}
        <div>
          <label
            htmlFor="filter-advisor-status"
            className="block text-xs font-medium text-slate-300 mb-1"
          >
            Estado
          </label>
          <select
            id="filter-advisor-status"
            value={filters.status || 'all'}
            onChange={(e) =>
              onFilterChange({
                ...filters,
                status: e.target.value as AdvisorStatus | 'all',
              })
            }
            className="w-full px-2.5 py-1.5 bg-slate-950/80 border border-slate-700/80 rounded-lg text-xs text-slate-100 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
          >
            <option value="all">Todos</option>
            <option value="active">Activos</option>
            <option value="inactive">Inactivos</option>
          </select>
        </div>
      </div>

      {hasActiveFilters && (
        <div className="flex justify-end pt-1">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={onClearFilters}
            className="text-xs text-slate-400 hover:text-slate-200 gap-1"
          >
            <X className="w-3.5 h-3.5" aria-hidden="true" />
            Limpiar filtros
          </Button>
        </div>
      )}
    </div>
  )
}
