import { Card, CardContent } from '@/components/ui/Card'
import type { CatalogSummaryMetrics } from '../catalog.types'
import { formatPriceCOP } from '../catalog.adapters'
import { Bike, Boxes, DollarSign, Tag } from 'lucide-react'

interface CatalogSummaryCardsProps {
  metrics: CatalogSummaryMetrics
}

export function CatalogSummaryCards({ metrics }: CatalogSummaryCardsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* 1. Total Modelos */}
      <Card className="border-slate-800/80 bg-slate-900/60">
        <CardContent className="p-4 flex flex-col justify-between h-full">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Modelos Activos</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-950/60 border border-indigo-800/40 flex items-center justify-center text-indigo-400">
              <Bike className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-slate-100">
              {metrics.totalModels}
            </div>
            <p className="text-[11px] text-slate-400 mt-1">Líneas en catálogo oficial</p>
          </div>
        </CardContent>
      </Card>

      {/* 2. Marcas */}
      <Card className="border-slate-800/80 bg-slate-900/60">
        <CardContent className="p-4 flex flex-col justify-between h-full">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Marcas Representadas</span>
            <div className="w-8 h-8 rounded-lg bg-cyan-950/60 border border-cyan-800/40 flex items-center justify-center text-cyan-400">
              <Tag className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-slate-100">
              {metrics.activeBrands}
            </div>
            <p className="text-[11px] text-slate-400 mt-1">Fabricantes autorizados</p>
          </div>
        </CardContent>
      </Card>

      {/* 3. Unidades en Inventario */}
      <Card className="border-slate-800/80 bg-slate-900/60">
        <CardContent className="p-4 flex flex-col justify-between h-full">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Unidades Disponibles</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-950/60 border border-emerald-800/40 flex items-center justify-center text-emerald-400">
              <Boxes className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-emerald-100">
              {metrics.totalUnits}
            </div>
            <p className="text-[11px] text-emerald-300/80 mt-1 font-medium">
              Stock total reportado
            </p>
          </div>
        </CardContent>
      </Card>

      {/* 4. Rango de Precios */}
      <Card className="border-slate-800/80 bg-slate-900/60">
        <CardContent className="p-4 flex flex-col justify-between h-full">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Rango de Precios</span>
            <div className="w-8 h-8 rounded-lg bg-amber-950/60 border border-amber-800/40 flex items-center justify-center text-amber-400">
              <DollarSign className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-sm font-bold text-slate-100 truncate">
              {formatPriceCOP(metrics.minPrice)}
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5">
              hasta {formatPriceCOP(metrics.maxPrice)}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
