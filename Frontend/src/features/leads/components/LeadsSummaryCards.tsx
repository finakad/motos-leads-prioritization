import type { LeadsSummaryStats } from '../lead.types'
import { Card } from '@/components/ui/Card'
import { Users, Flame, AlertCircle, Clock } from 'lucide-react'

interface LeadsSummaryCardsProps {
  stats: LeadsSummaryStats
}

export function LeadsSummaryCards({ stats }: LeadsSummaryCardsProps) {
  return (
    <section aria-label="Resumen de leads visibles" className="grid grid-cols-2 lg:grid-cols-4 gap-3.5">
      {/* Total Leads */}
      <Card className="p-4 bg-slate-900/60 border-slate-800">
        <div className="flex items-center justify-between text-slate-400">
          <span className="text-xs font-semibold uppercase tracking-wider">Leads Visibles</span>
          <Users className="w-4 h-4 text-cyan-400" aria-hidden="true" />
        </div>
        <div className="text-2xl font-bold text-slate-100 font-mono mt-1.5">
          {stats.total}
        </div>
        <div className="text-[11px] text-slate-500 mt-0.5">Prospectos filtrados</div>
      </Card>

      {/* Prioridad Alta */}
      <Card className="p-4 bg-slate-900/60 border-rose-950/40">
        <div className="flex items-center justify-between text-rose-400">
          <span className="text-xs font-semibold uppercase tracking-wider">Prioridad Alta</span>
          <Flame className="w-4 h-4 text-rose-400" aria-hidden="true" />
        </div>
        <div className="text-2xl font-bold text-rose-400 font-mono mt-1.5">
          {stats.high}
        </div>
        <div className="text-[11px] text-slate-500 mt-0.5">Atención urgente</div>
      </Card>

      {/* Prioridad Media */}
      <Card className="p-4 bg-slate-900/60 border-amber-950/40">
        <div className="flex items-center justify-between text-amber-400">
          <span className="text-xs font-semibold uppercase tracking-wider">Prioridad Media</span>
          <AlertCircle className="w-4 h-4 text-amber-400" aria-hidden="true" />
        </div>
        <div className="text-2xl font-bold text-amber-400 font-mono mt-1.5">
          {stats.medium}
        </div>
        <div className="text-[11px] text-slate-500 mt-0.5">En seguimiento regular</div>
      </Card>

      {/* Prioridad Baja */}
      <Card className="p-4 bg-slate-900/60 border-slate-800">
        <div className="flex items-center justify-between text-slate-400">
          <span className="text-xs font-semibold uppercase tracking-wider">Prioridad Baja</span>
          <Clock className="w-4 h-4 text-slate-400" aria-hidden="true" />
        </div>
        <div className="text-2xl font-bold text-slate-300 font-mono mt-1.5">
          {stats.low}
        </div>
        <div className="text-[11px] text-slate-500 mt-0.5">Baja maduración o frío</div>
      </Card>
    </section>
  )
}
