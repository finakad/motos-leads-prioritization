import { Card, CardContent } from '@/components/ui/Card'
import type { DashboardKpiMetrics } from '../dashboard.types'
import { Users, Flame, Target, ShieldAlert, Award } from 'lucide-react'

interface DashboardKpiCardsProps {
  metrics: DashboardKpiMetrics
}

export function DashboardKpiCards({ metrics }: DashboardKpiCardsProps) {
  const highPercentage =
    metrics.totalLeads > 0
      ? Math.round((metrics.highPriorityLeads / metrics.totalLeads) * 1000) / 10
      : 0

  const mediumPercentage =
    metrics.totalLeads > 0
      ? Math.round((metrics.mediumPriorityLeads / metrics.totalLeads) * 1000) / 10
      : 0

  const lowPercentage =
    metrics.totalLeads > 0
      ? Math.round((metrics.lowPriorityLeads / metrics.totalLeads) * 1000) / 10
      : 0

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      {/* 1. Total Leads */}
      <Card className="border-slate-800/80 bg-slate-900/60">
        <CardContent className="p-4 flex flex-col justify-between h-full">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Total Leads</span>
            <div className="w-8 h-8 rounded-lg bg-cyan-950/60 border border-cyan-800/40 flex items-center justify-center text-cyan-400">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-slate-100">
              {metrics.totalLeads.toLocaleString('es-CO')}
            </div>
            <p className="text-[11px] text-slate-400 mt-1">
              {metrics.isTotalCensus
                ? 'Censo total de la empresa'
                : `Muestra de ${metrics.sampleSize} leads`}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* 2. Prioridad Alta */}
      <Card className="border-rose-900/40 bg-rose-950/10">
        <CardContent className="p-4 flex flex-col justify-between h-full">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-rose-300">Prioridad Alta</span>
            <div className="w-8 h-8 rounded-lg bg-rose-950/60 border border-rose-800/40 flex items-center justify-center text-rose-400">
              <Flame className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-rose-100">
              {metrics.highPriorityLeads.toLocaleString('es-CO')}
            </div>
            <p className="text-[11px] text-rose-300/80 mt-1 font-medium">
              {highPercentage}% de la cartera activa
            </p>
          </div>
        </CardContent>
      </Card>

      {/* 3. Prioridad Media */}
      <Card className="border-amber-900/40 bg-amber-950/10">
        <CardContent className="p-4 flex flex-col justify-between h-full">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-amber-300">Prioridad Media</span>
            <div className="w-8 h-8 rounded-lg bg-amber-950/60 border border-amber-800/40 flex items-center justify-center text-amber-400">
              <Target className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-amber-100">
              {metrics.mediumPriorityLeads.toLocaleString('es-CO')}
            </div>
            <p className="text-[11px] text-amber-300/80 mt-1 font-medium">
              {mediumPercentage}% en seguimiento comercial
            </p>
          </div>
        </CardContent>
      </Card>

      {/* 4. Prioridad Baja */}
      <Card className="border-slate-800/80 bg-slate-900/60">
        <CardContent className="p-4 flex flex-col justify-between h-full">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Prioridad Baja</span>
            <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700/60 flex items-center justify-center text-slate-400">
              <ShieldAlert className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-slate-100">
              {metrics.lowPriorityLeads.toLocaleString('es-CO')}
            </div>
            <p className="text-[11px] text-slate-400 mt-1 font-medium">
              {lowPercentage}% baja propensión
            </p>
          </div>
        </CardContent>
      </Card>

      {/* 5. Score Promedio */}
      <Card className="border-emerald-900/40 bg-emerald-950/10">
        <CardContent className="p-4 flex flex-col justify-between h-full">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-emerald-300">Score Promedio</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-950/60 border border-emerald-800/40 flex items-center justify-center text-emerald-400">
              <Award className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-emerald-100">
              {metrics.averageScore !== null ? `${metrics.averageScore}` : 'N/D'}
              <span className="text-xs font-normal text-emerald-300/70 ml-1">/ 100</span>
            </div>
            <p className="text-[11px] text-emerald-300/80 mt-1 font-medium">
              Calidad global de leads
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
