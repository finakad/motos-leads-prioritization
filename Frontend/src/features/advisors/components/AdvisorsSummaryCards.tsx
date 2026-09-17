import type { AdvisorsGeneralStats } from '../advisor.types'
import { Card } from '@/components/ui/Card'
import { Users, UserCheck, UserX, Gauge, FolderKanban, Flame } from 'lucide-react'

interface AdvisorsSummaryCardsProps {
  stats: AdvisorsGeneralStats
}

export function AdvisorsSummaryCards({ stats }: AdvisorsSummaryCardsProps) {
  return (
    <section
      aria-label="Indicadores generales de asesores y capacidad"
      className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3"
    >
      {/* 1. Total Asesores */}
      <Card className="p-3.5 bg-slate-900/60 border-slate-800">
        <div className="flex items-center justify-between text-slate-400">
          <span className="text-[11px] font-semibold uppercase tracking-wider">Asesores</span>
          <Users className="w-3.5 h-3.5 text-cyan-400" aria-hidden="true" />
        </div>
        <div className="text-xl font-bold text-slate-100 font-mono mt-1">
          {stats.totalAdvisors}
        </div>
        <div className="text-[10px] text-slate-500 mt-0.5">Visibles en sede</div>
      </Card>

      {/* 2. Asesores Activos */}
      <Card className="p-3.5 bg-slate-900/60 border-slate-800">
        <div className="flex items-center justify-between text-emerald-400">
          <span className="text-[11px] font-semibold uppercase tracking-wider">Activos</span>
          <UserCheck className="w-3.5 h-3.5" aria-hidden="true" />
        </div>
        <div className="text-xl font-bold text-emerald-400 font-mono mt-1">
          {stats.activeAdvisors}
        </div>
        <div className="text-[10px] text-slate-500 mt-0.5">Disponibles</div>
      </Card>

      {/* 3. Asesores Inactivos */}
      <Card className="p-3.5 bg-slate-900/60 border-slate-800">
        <div className="flex items-center justify-between text-slate-400">
          <span className="text-[11px] font-semibold uppercase tracking-wider">Inactivos</span>
          <UserX className="w-3.5 h-3.5 text-slate-500" aria-hidden="true" />
        </div>
        <div className="text-xl font-bold text-slate-400 font-mono mt-1">
          {stats.inactiveAdvisors}
        </div>
        <div className="text-[10px] text-slate-500 mt-0.5">Fuera de turno</div>
      </Card>

      {/* 4. Capacidad Diaria Total */}
      <Card className="p-3.5 bg-slate-900/60 border-amber-950/40">
        <div className="flex items-center justify-between text-amber-400">
          <span className="text-[11px] font-semibold uppercase tracking-wider">Capacidad/Día</span>
          <Gauge className="w-3.5 h-3.5" aria-hidden="true" />
        </div>
        <div className="text-xl font-bold text-amber-300 font-mono mt-1">
          {stats.totalActiveDailyCapacity}
        </div>
        <div className="text-[10px] text-slate-500 mt-0.5">Leads máx. activos</div>
      </Card>

      {/* 5. Total Leads en Puntos Visibles */}
      <Card className="p-3.5 bg-slate-900/60 border-slate-800">
        <div className="flex items-center justify-between text-cyan-400">
          <span className="text-[11px] font-semibold uppercase tracking-wider">Total Leads</span>
          <FolderKanban className="w-3.5 h-3.5" aria-hidden="true" />
        </div>
        <div className="text-xl font-bold text-cyan-300 font-mono mt-1">
          {stats.totalLeadsAtVisibleSalesPoints}
        </div>
        <div className="text-[10px] text-slate-500 mt-0.5">En sedes visibles</div>
      </Card>

      {/* 6. Total Leads Alta Prioridad */}
      <Card className="p-3.5 bg-slate-900/60 border-rose-950/40">
        <div className="flex items-center justify-between text-rose-400">
          <span className="text-[11px] font-semibold uppercase tracking-wider">Alta Prioridad</span>
          <Flame className="w-3.5 h-3.5" aria-hidden="true" />
        </div>
        <div className="text-xl font-bold text-rose-400 font-mono mt-1">
          {stats.totalHighPriorityLeadsAtVisibleSalesPoints}
        </div>
        <div className="text-[10px] text-slate-500 mt-0.5">Prospectos calientes</div>
      </Card>
    </section>
  )
}
