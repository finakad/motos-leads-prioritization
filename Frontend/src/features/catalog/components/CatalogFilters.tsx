import type { CatalogFiltersState } from '../catalog.types'
import { Search, X, Filter } from 'lucide-react'

interface CatalogFiltersProps {
  filters: CatalogFiltersState
  onChange: (newFilters: CatalogFiltersState) => void
  brands: string[]
  segments: string[]
  salesPoints: string[]
  onReset: () => void
}

export function CatalogFilters({
  filters,
  onChange,
  brands,
  segments,
  salesPoints,
  onReset,
}: CatalogFiltersProps) {
  const hasActiveFilters =
    Boolean(filters.search) ||
    filters.brand !== 'all' ||
    filters.segment !== 'all' ||
    filters.salesPointId !== 'all'

  return (
    <div className="bg-slate-900/80 backdrop-blur-sm border border-slate-800/80 rounded-xl p-4 shadow-sm space-y-3">
      <div className="flex flex-col lg:flex-row items-stretch lg:items-center gap-3">
        {/* Barra de Búsqueda */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Buscar por modelo, marca o SKU (ej. Twister, MT-03, Honda)..."
            value={filters.search}
            onChange={(e) => onChange({ ...filters, search: e.target.value })}
            className="w-full bg-slate-950/60 border border-slate-800 rounded-lg pl-9 pr-8 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-500 focus:border-cyan-500 transition-colors"
          />
          {filters.search && (
            <button
              type="button"
              onClick={() => onChange({ ...filters, search: '' })}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Selectores de Filtro */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
          {/* Marca */}
          <select
            value={filters.brand}
            onChange={(e) => onChange({ ...filters, brand: e.target.value })}
            className="bg-slate-950/60 border border-slate-800 rounded-lg px-2.5 py-2 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-cyan-500"
          >
            <option value="all">Todas las marcas</option>
            {brands.map((b) => (
              <option key={b} value={b}>
                {b}
              </option>
            ))}
          </select>

          {/* Segmento */}
          <select
            value={filters.segment}
            onChange={(e) => onChange({ ...filters, segment: e.target.value })}
            className="bg-slate-950/60 border border-slate-800 rounded-lg px-2.5 py-2 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-cyan-500"
          >
            <option value="all">Todos los segmentos</option>
            {segments.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>

          {/* Sede / Punto de venta */}
          <select
            value={filters.salesPointId}
            onChange={(e) => onChange({ ...filters, salesPointId: e.target.value })}
            className="bg-slate-950/60 border border-slate-800 rounded-lg px-2.5 py-2 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-cyan-500"
          >
            <option value="all">Todas las sedes</option>
            {salesPoints.map((sp) => (
              <option key={sp} value={sp}>
                {sp}
              </option>
            ))}
          </select>

          {/* Ordenamiento */}
          <select
            value={filters.sortBy}
            onChange={(e) =>
              onChange({
                ...filters,
                sortBy: e.target.value as CatalogFiltersState['sortBy'],
              })
            }
            className="bg-slate-950/60 border border-slate-800 rounded-lg px-2.5 py-2 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-cyan-500"
          >
            <option value="price-asc">Precio: menor a mayor</option>
            <option value="price-desc">Precio: mayor a menor</option>
            <option value="cc-asc">Cilindraje: menor a mayor</option>
            <option value="cc-desc">Cilindraje: mayor a menor</option>
            <option value="name">Alfabético (A-Z)</option>
          </select>
        </div>

        {/* Botón limpiar */}
        {hasActiveFilters && (
          <button
            type="button"
            onClick={onReset}
            className="flex items-center justify-center gap-1 text-xs text-rose-400 hover:text-rose-300 px-3 py-2 border border-rose-900/40 bg-rose-950/20 rounded-lg transition-colors whitespace-nowrap"
          >
            <Filter className="w-3.5 h-3.5" />
            Limpiar
          </button>
        )}
      </div>
    </div>
  )
}
