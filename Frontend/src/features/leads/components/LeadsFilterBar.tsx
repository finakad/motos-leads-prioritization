import { Search, X } from 'lucide-react'
import type { LeadsFilter, LeadPriority, LeadStatus, LeadChannel } from '../types/lead'
import { Button } from '@/components/ui/Button'

interface LeadsFilterBarProps {
  filter: LeadsFilter
  onFilterChange: (newFilter: LeadsFilter) => void
  onReset: () => void
}

export function LeadsFilterBar({
  filter,
  onFilterChange,
  onReset,
}: LeadsFilterBarProps) {
  const hasActiveFilters = Boolean(
    filter.search ||
      (filter.priority && filter.priority !== 'TODAS') ||
      (filter.status && filter.status !== 'TODOS') ||
      (filter.channel && filter.channel !== 'TODOS')
  )

  return (
    <div className="bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-slate-800/80 space-y-3">
      <div className="flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between">
        {/* Search input */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Buscar por nombre, teléfono o modelo de moto..."
            value={filter.search || ''}
            onChange={(e) => onFilterChange({ ...filter, search: e.target.value })}
            className="w-full pl-9 pr-4 py-2 bg-slate-950/70 border border-slate-700/70 rounded-lg text-sm text-slate-100 placeholder:text-slate-400 focus:outline-none focus:border-amber-500/80 focus:ring-1 focus:ring-amber-500/80 transition-colors"
          />
        </div>

        {/* Filter dropdowns */}
        <div className="flex flex-wrap gap-2 items-center">
          {/* Priority */}
          <div className="flex items-center gap-1.5">
            <label className="text-xs text-slate-400 hidden sm:inline">Prioridad:</label>
            <select
              value={filter.priority || 'TODAS'}
              onChange={(e) =>
                onFilterChange({
                  ...filter,
                  priority: e.target.value as LeadPriority | 'TODAS',
                })
              }
              className="bg-slate-950/70 border border-slate-700/70 text-xs text-slate-200 rounded-lg px-2.5 py-2 focus:outline-none focus:border-amber-500"
            >
              <option value="TODAS">Todas las prioridades</option>
              <option value="ALTA">Alta</option>
              <option value="MEDIA">Media</option>
              <option value="BAJA">Baja</option>
            </select>
          </div>

          {/* Status */}
          <div className="flex items-center gap-1.5">
            <label className="text-xs text-slate-400 hidden sm:inline">Estado:</label>
            <select
              value={filter.status || 'TODOS'}
              onChange={(e) =>
                onFilterChange({
                  ...filter,
                  status: e.target.value as LeadStatus | 'TODOS',
                })
              }
              className="bg-slate-950/70 border border-slate-700/70 text-xs text-slate-200 rounded-lg px-2.5 py-2 focus:outline-none focus:border-amber-500"
            >
              <option value="TODOS">Todos los estados</option>
              <option value="NUEVO">Nuevo</option>
              <option value="CONTACTADO">Contactado</option>
              <option value="EN_GESTION">En Gestión</option>
              <option value="CALIFICADO">Calificado</option>
              <option value="DESCARTADO">Descartado</option>
              <option value="VENTA_CERRADA">Venta Cerrada</option>
            </select>
          </div>

          {/* Channel */}
          <div className="flex items-center gap-1.5">
            <label className="text-xs text-slate-400 hidden sm:inline">Canal:</label>
            <select
              value={filter.channel || 'TODOS'}
              onChange={(e) =>
                onFilterChange({
                  ...filter,
                  channel: e.target.value as LeadChannel | 'TODOS',
                })
              }
              className="bg-slate-950/70 border border-slate-700/70 text-xs text-slate-200 rounded-lg px-2.5 py-2 focus:outline-none focus:border-amber-500"
            >
              <option value="TODOS">Todos los canales</option>
              <option value="WHATSAPP">WhatsApp</option>
              <option value="WEB">Sitio Web</option>
              <option value="INSTAGRAM">Instagram</option>
              <option value="FACEBOOK">Facebook</option>
              <option value="CONCESIONARIO">Concesionario</option>
            </select>
          </div>

          {hasActiveFilters && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onReset}
              className="text-slate-400 hover:text-slate-200 gap-1"
            >
              <X className="w-3.5 h-3.5" />
              Limpiar
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
