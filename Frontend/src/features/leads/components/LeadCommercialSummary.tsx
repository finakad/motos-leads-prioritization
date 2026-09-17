import type { LeadDetail } from '../lead.types'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { formatColombiaDate } from '@/lib/utils'
import { Briefcase, Bike, Store, MapPin, Megaphone, Calendar, Clock, Globe } from 'lucide-react'

interface LeadCommercialSummaryProps {
  lead: LeadDetail
}

function displayValue(value: string | null | undefined): string {
  if (!value || value.trim().length === 0) {
    return 'No disponible'
  }
  return value
}

export function LeadCommercialSummary({ lead }: LeadCommercialSummaryProps) {
  return (
    <Card className="bg-slate-900/80 border-slate-800">
      <CardHeader className="pb-3 border-b border-slate-800/80">
        <CardTitle className="text-base font-semibold text-slate-100 flex items-center gap-2">
          <Briefcase className="w-4 h-4 text-cyan-400" aria-hidden="true" />
          Resumen comercial
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-4">
        <dl className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          {/* Canal */}
          <div className="space-y-1">
            <dt className="text-slate-400 flex items-center gap-1.5 font-medium">
              <Globe className="w-3.5 h-3.5 text-slate-500" aria-hidden="true" />
              Canal
            </dt>
            <dd className="text-slate-100 font-semibold">{displayValue(lead.channel)}</dd>
          </div>

          {/* Estado de gestión */}
          <div className="space-y-1">
            <dt className="text-slate-400 flex items-center gap-1.5 font-medium">
              <Clock className="w-3.5 h-3.5 text-slate-500" aria-hidden="true" />
              Estado de gestión
            </dt>
            <dd className="text-slate-100 font-semibold">
              <span className="inline-flex px-2 py-0.5 rounded text-[11px] font-medium bg-slate-800 text-slate-200 border border-slate-700/60">
                {displayValue(lead.managementStatus)}
              </span>
            </dd>
          </div>

          {/* Modelo de interés */}
          <div className="space-y-1">
            <dt className="text-slate-400 flex items-center gap-1.5 font-medium">
              <Bike className="w-3.5 h-3.5 text-amber-400" aria-hidden="true" />
              Modelo de interés
            </dt>
            <dd className="text-amber-300 font-semibold">{displayValue(lead.modelInterestText)}</dd>
          </div>

          {/* Punto de venta */}
          <div className="space-y-1">
            <dt className="text-slate-400 flex items-center gap-1.5 font-medium">
              <Store className="w-3.5 h-3.5 text-slate-500" aria-hidden="true" />
              Punto de venta
            </dt>
            <dd className="text-slate-100 font-mono font-medium">{displayValue(lead.salesPointId)}</dd>
          </div>

          {/* Ciudad */}
          <div className="space-y-1">
            <dt className="text-slate-400 flex items-center gap-1.5 font-medium">
              <MapPin className="w-3.5 h-3.5 text-slate-500" aria-hidden="true" />
              Ciudad
            </dt>
            <dd className="text-slate-200">{displayValue(lead.city)}</dd>
          </div>

          {/* Campaña */}
          <div className="space-y-1">
            <dt className="text-slate-400 flex items-center gap-1.5 font-medium">
              <Megaphone className="w-3.5 h-3.5 text-slate-500" aria-hidden="true" />
              Campaña
            </dt>
            <dd className="text-slate-200">{displayValue(lead.campaign)}</dd>
          </div>

          {/* Fecha de registro */}
          <div className="space-y-1">
            <dt className="text-slate-400 flex items-center gap-1.5 font-medium">
              <Calendar className="w-3.5 h-3.5 text-slate-500" aria-hidden="true" />
              Fecha de registro
            </dt>
            <dd className="text-slate-200">{formatColombiaDate(lead.registeredAt)}</dd>
          </div>

          {/* Fecha primer contacto */}
          <div className="space-y-1">
            <dt className="text-slate-400 flex items-center gap-1.5 font-medium">
              <Calendar className="w-3.5 h-3.5 text-slate-500" aria-hidden="true" />
              Primer contacto
            </dt>
            <dd className="text-slate-200">{lead.firstContactAt ? formatColombiaDate(lead.firstContactAt) : 'No disponible'}</dd>
          </div>
        </dl>
      </CardContent>
    </Card>
  )
}
