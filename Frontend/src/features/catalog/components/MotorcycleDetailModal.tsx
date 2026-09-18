import type { Motorcycle } from '../catalog.types'
import { formatPriceCOP } from '../catalog.adapters'
import { Badge } from '@/components/ui/Badge'
import { X, Bike, Gauge, DollarSign, Layers, MapPin, CheckCircle2 } from 'lucide-react'

interface MotorcycleDetailModalProps {
  motorcycle: Motorcycle | null
  onClose: () => void
}

export function MotorcycleDetailModal({
  motorcycle,
  onClose,
}: MotorcycleDetailModalProps) {
  if (!motorcycle) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
        {/* Cabecera del Modal */}
        <div className="px-6 py-4 border-b border-slate-800/80 flex items-center justify-between bg-slate-950/40">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-950/60 border border-cyan-800/50 flex items-center justify-center text-cyan-400">
              <Bike className="w-5 h-5" />
            </div>
            <div>
              <span className="text-xs font-mono font-bold uppercase tracking-wider text-cyan-400">
                {motorcycle.brand}
              </span>
              <h2 className="text-lg font-bold text-slate-100">{motorcycle.line}</h2>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="w-8 h-8 rounded-lg bg-slate-800 text-slate-400 hover:text-slate-100 hover:bg-slate-700 flex items-center justify-center transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Cuerpo del Modal */}
        <div className="p-6 space-y-5">
          {/* Precio y estado */}
          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center justify-between">
            <div>
              <span className="text-xs text-slate-400 font-medium">Precio Oficial Lista</span>
              <div className="text-2xl font-bold text-emerald-400 font-mono">
                {formatPriceCOP(motorcycle.listPrice)}
              </div>
            </div>
            <Badge variant="success" size="md" className="normal-case font-semibold">
              <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
              Catálogo Vigente
            </Badge>
          </div>

          {/* Especificaciones técnicas */}
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-3 rounded-lg bg-slate-950/40 border border-slate-800/60 space-y-1">
              <div className="text-slate-400 flex items-center gap-1.5">
                <Gauge className="w-3.5 h-3.5 text-cyan-400" />
                Cilindraje
              </div>
              <div className="text-sm font-bold text-slate-100">
                {motorcycle.engineDisplacementCc} cc
              </div>
            </div>

            <div className="p-3 rounded-lg bg-slate-950/40 border border-slate-800/60 space-y-1">
              <div className="text-slate-400 flex items-center gap-1.5">
                <Bike className="w-3.5 h-3.5 text-indigo-400" />
                Segmento
              </div>
              <div className="text-sm font-bold text-slate-100">
                {motorcycle.segment}
              </div>
            </div>

            <div className="p-3 rounded-lg bg-slate-950/40 border border-slate-800/60 space-y-1">
              <div className="text-slate-400 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-amber-400" />
                Unidades en Stock
              </div>
              <div className="text-sm font-bold text-slate-100">
                {motorcycle.reportedAvailableUnits} unidades
              </div>
            </div>

            <div className="p-3 rounded-lg bg-slate-950/40 border border-slate-800/60 space-y-1">
              <div className="text-slate-400 flex items-center gap-1.5">
                <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
                Código SKU
              </div>
              <div className="text-sm font-mono font-bold text-slate-100">
                {motorcycle.sku}
              </div>
            </div>
          </div>

          {/* Sedes con Disponibilidad */}
          <div className="space-y-2">
            <div className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-cyan-400" />
              Disponibilidad en Sedes de la Empresa ({motorcycle.availableSalesPoints.length}):
            </div>
            {motorcycle.availableSalesPoints.length === 0 ? (
              <p className="text-xs text-slate-500 italic p-3 rounded-lg bg-slate-950/40 border border-slate-800/60">
                Actualmente no hay unidades disponibles de este modelo en las sedes de esta empresa.
              </p>
            ) : (
              <div className="flex flex-wrap gap-2 p-3 rounded-lg bg-slate-950/40 border border-slate-800/60">
                {motorcycle.availableSalesPoints.map((sp) => (
                  <span
                    key={sp}
                    className="px-2.5 py-1 rounded-md text-xs font-mono font-bold bg-cyan-950/60 text-cyan-300 border border-cyan-800/40"
                  >
                    {sp}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Pie del modal */}
        <div className="px-6 py-4 border-t border-slate-800/80 bg-slate-950/40 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors"
          >
            Cerrar Ficha
          </button>
        </div>
      </div>
    </div>
  )
}
