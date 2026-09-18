import { Card, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import type { Motorcycle } from '../catalog.types'
import { formatPriceCOP } from '../catalog.adapters'
import { Gauge, MapPin, Layers, Info } from 'lucide-react'

interface CatalogCardProps {
  motorcycle: Motorcycle
  onSelect: (motorcycle: Motorcycle) => void
}

export function CatalogCard({ motorcycle, onSelect }: CatalogCardProps) {
  return (
    <Card className="border-slate-800/80 bg-slate-900/60 hover:border-slate-700/80 transition-all duration-200 hover:shadow-lg hover:shadow-cyan-950/10 flex flex-col justify-between group">
      <CardContent className="p-5 flex flex-col justify-between h-full space-y-4">
        {/* Cabecera de la tarjeta: Marca, Segmento y SKU */}
        <div>
          <div className="flex items-center justify-between gap-2 mb-2">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-cyan-400">
              {motorcycle.brand}
            </span>
            <Badge variant="neutral" size="sm" className="text-[10px] normal-case">
              {motorcycle.segment}
            </Badge>
          </div>

          <h3 className="text-base font-bold text-slate-100 group-hover:text-cyan-300 transition-colors line-clamp-1">
            {motorcycle.line}
          </h3>
          <div className="text-[11px] font-mono text-slate-500 mt-0.5">
            SKU: {motorcycle.sku}
          </div>
        </div>

        {/* Especificaciones técnicas rápidas */}
        <div className="grid grid-cols-2 gap-2 py-2.5 border-y border-slate-800/60 text-xs">
          <div className="flex items-center gap-1.5 text-slate-300">
            <Gauge className="w-3.5 h-3.5 text-slate-400" />
            <span className="font-semibold">{motorcycle.engineDisplacementCc} cc</span>
          </div>

          <div className="flex items-center gap-1.5 text-slate-300">
            <Layers className="w-3.5 h-3.5 text-slate-400" />
            <span>
              Stock:{' '}
              <strong className="text-emerald-400">
                {motorcycle.reportedAvailableUnits}
              </strong>
            </span>
          </div>
        </div>

        {/* Sedes con disponibilidad */}
        <div>
          <div className="text-[11px] text-slate-400 font-medium flex items-center gap-1 mb-1.5">
            <MapPin className="w-3 h-3 text-cyan-400" />
            Sedes disponibles ({motorcycle.availableSalesPoints.length}):
          </div>
          <div className="flex flex-wrap gap-1">
            {motorcycle.availableSalesPoints.length === 0 ? (
              <span className="text-[11px] text-slate-500 italic">
                Sin disponibilidad en esta empresa
              </span>
            ) : (
              motorcycle.availableSalesPoints.map((sp) => (
                <span
                  key={sp}
                  className="px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold bg-slate-800 text-slate-300 border border-slate-700/60"
                >
                  {sp}
                </span>
              ))
            )}
          </div>
        </div>

        {/* Precio y Acción */}
        <div className="pt-2 flex items-center justify-between border-t border-slate-800/60">
          <div>
            <div className="text-[10px] uppercase font-semibold text-slate-400">
              Precio Lista
            </div>
            <div className="text-base font-bold text-emerald-400 font-mono">
              {formatPriceCOP(motorcycle.listPrice)}
            </div>
          </div>

          <button
            type="button"
            onClick={() => onSelect(motorcycle)}
            className="inline-flex items-center gap-1 text-xs font-semibold px-3 py-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 transition-colors"
          >
            <Info className="w-3.5 h-3.5" />
            Ficha
          </button>
        </div>
      </CardContent>
    </Card>
  )
}
