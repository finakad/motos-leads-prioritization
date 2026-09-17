import type { LeadsFilterParams, LeadPriority } from '../lead.types'
import { Search, X } from 'lucide-react'
import { Button } from '@/components/ui/Button'

interface LeadsFiltersProps {
  filters: LeadsFilterParams
  onFilterChange: (newFilters: LeadsFilterParams) => void
  onClearFilters: () => void
  channels: string[]
  statuses: string[]
  salesPoints: string[]
}

export function LeadsFilters({
  filters,
  onFilterChange,
  onClearFilters,
  channels,
  statuses,
  salesPoints,
}: LeadsFiltersProps) {
  const hasActiveFilters = Boolean(
    (filters.search && filters.search.trim().length > 0) ||
      (filters.priority && filters.priority !== 'all') ||
      (filters.channel && filters.channel !== 'all') ||
      (filters.managementStatus && filters.managementStatus !== 'all') ||
      (filters.salesPointId && filters.salesPointId !== 'all')
  )

  return (
    <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {/* Búsqueda por nombre o ID */}
        <div className="sm:col-span-2 lg:col-span-1">
          <label
            htmlFor="filter-search"
            className="block text-xs font-medium text-slate-300 mb-1"
          >
            Buscar cliente o ID
          </label>
          <div className="relative">
            <Search
              className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2"
              aria-hidden="true"
            />
            <input
              id="filter-search"
              type="text"
              placeholder="Ej. Carlos o LD-00101"
              value={filters.search || ''}
              onChange={(e) =>
                onFilterChange({ ...filters, search: e.target.value })
              }
              className="w-full pl-9 pr-3 py-1.5 bg-slate-950/80 border border-slate-700/80 rounded-lg text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
            />
          </div>
        </div>

        {/* Prioridad */}
        <div>
          <label
            htmlFor="filter-priority"
            className="block text-xs font-medium text-slate-300 mb-1"
          >
            Prioridad
          </label>
          <select
            id="filter-priority"
            value={filters.priority || 'all'}
            onChange={(e) =>
              onFilterChange({
                ...filters,
                priority: e.target.value as LeadPriority | 'all',
              })
            }
            className="w-full px-2.5 py-1.5 bg-slate-950/80 border border-slate-700/80 rounded-lg text-xs text-slate-100 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
          >
            <option value="all">Todas las prioridades</option>
            <option value="high">Alta</option>
            <option value="medium">Media</option>
            <option value="low">Baja</option>
          </select>
        </div>

        {/* Canal */}
        <div>
          <label
            htmlFor="filter-channel"
            className="block text-xs font-medium text-slate-300 mb-1"
          >
            Canal
          </label>
          <select
            id="filter-channel"
            value={filters.channel || 'all'}
            onChange={(e) =>
              onFilterChange({
                ...filters,
                channel: e.target.value,
              })
            }
            className="w-full px-2.5 py-1.5 bg-slate-950/80 border border-slate-700/80 rounded-lg text-xs text-slate-100 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
          >
            <option value="all">Todos los canales</option>
            {channels.map((channel) => (
              <option key={channel} value={channel}>
                {channel}
              </option>
            ))}
          </select>
        </div>

        {/* Estado de gestión */}
        <div>
          <label
            htmlFor="filter-status"
            className="block text-xs font-medium text-slate-300 mb-1"
          >
            Estado de gestión
          </label>
          <select
            id="filter-status"
            value={filters.managementStatus || 'all'}
            onChange={(e) =>
              onFilterChange({
                ...filters,
                managementStatus: e.target.value,
              })
            }
            className="w-full px-2.5 py-1.5 bg-slate-950/80 border border-slate-700/80 rounded-lg text-xs text-slate-100 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
          >
            <option value="all">Todos los estados</option>
            {statuses.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>

        {/* Punto de venta */}
        <div>
          <label
            htmlFor="filter-sales-point"
            className="block text-xs font-medium text-slate-300 mb-1"
          >
            Punto de venta
          </label>
          <select
            id="filter-sales-point"
            value={filters.salesPointId || 'all'}
            onChange={(e) =>
              onFilterChange({
                ...filters,
                salesPointId: e.target.value,
              })
            }
            className="w-full px-2.5 py-1.5 bg-slate-950/80 border border-slate-700/80 rounded-lg text-xs text-slate-100 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
          >
            <option value="all">Todos los puntos</option>
            {salesPoints.map((sp) => (
              <option key={sp} value={sp}>
                {sp}
              </option>
            ))}
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
