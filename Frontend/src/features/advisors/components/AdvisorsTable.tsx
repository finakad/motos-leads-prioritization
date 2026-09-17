import type { EnrichedAdvisor } from '../advisor.types'
import { AdvisorStatusBadge } from './AdvisorStatusBadge'
import { AdvisorCapacityUtilizationBadge } from './AdvisorCapacityUtilizationBadge'
import { formatColombiaDate } from '@/lib/utils'
import { Flame } from 'lucide-react'

interface AdvisorsTableProps {
  advisors: EnrichedAdvisor[]
}

export function AdvisorsTable({ advisors }: AdvisorsTableProps) {
  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden shadow-lg shadow-black/20">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse min-w-[980px]">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-950/60 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              <th scope="col" className="py-3 px-3.5">Asesor</th>
              <th scope="col" className="py-3 px-3.5">ID</th>
              <th scope="col" className="py-3 px-3.5">Empresa</th>
              <th scope="col" className="py-3 px-3.5">Punto de venta</th>
              <th scope="col" className="py-3 px-3.5">Estado</th>
              <th scope="col" className="py-3 px-3.5 text-center">Capacidad diaria</th>
              <th scope="col" className="py-3 px-3.5 text-center">Leads punto venta</th>
              <th scope="col" className="py-3 px-3.5 text-center">Prioridad alta</th>
              <th scope="col" className="py-3 px-3.5 text-center">Estimado/asesor</th>
              <th scope="col" className="py-3 px-3.5 text-center">Utilización estimada</th>
              <th scope="col" className="py-3 px-3.5 text-right">Fecha ingreso</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-xs">
            {advisors.map((advisor) => (
              <tr
                key={advisor.id}
                className="hover:bg-slate-800/40 transition-colors"
              >
                {/* Asesor */}
                <td className="py-3.5 px-3.5 font-semibold text-slate-100">
                  {advisor.fullName}
                </td>

                {/* ID */}
                <td className="py-3.5 px-3.5 font-mono text-[11px] text-slate-400">
                  {advisor.id}
                </td>

                {/* Empresa */}
                <td className="py-3.5 px-3.5 font-mono text-[11px] text-slate-300">
                  {advisor.companyId}
                </td>

                {/* Punto de venta */}
                <td className="py-3.5 px-3.5 font-mono text-[11px] text-slate-300">
                  {advisor.salesPointId}
                </td>

                {/* Estado */}
                <td className="py-3.5 px-3.5 whitespace-nowrap">
                  <AdvisorStatusBadge status={advisor.status} />
                </td>

                {/* Capacidad diaria */}
                <td className="py-3.5 px-3.5 text-center font-mono font-bold text-slate-200">
                  {advisor.dailyLeadCapacity} leads/día
                </td>

                {/* Leads del punto de venta */}
                <td className="py-3.5 px-3.5 text-center font-mono text-slate-300">
                  {advisor.workload.totalLeadsAtSalesPoint}
                </td>

                {/* Leads de prioridad alta */}
                <td className="py-3.5 px-3.5 text-center whitespace-nowrap">
                  {advisor.workload.highPriorityLeadsAtSalesPoint > 0 ? (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-rose-950/60 text-rose-400 border border-rose-900/60">
                      <Flame className="w-3 h-3" aria-hidden="true" />
                      {advisor.workload.highPriorityLeadsAtSalesPoint}
                    </span>
                  ) : (
                    <span className="text-slate-500 font-mono">0</span>
                  )}
                </td>

                {/* Estimado de leads por asesor */}
                <td className="py-3.5 px-3.5 text-center font-mono text-slate-200">
                  {advisor.workload.estimatedLeadsPerAdvisor > 0
                    ? `~${advisor.workload.estimatedLeadsPerAdvisor}`
                    : 'No disponible'}
                </td>

                {/* Utilización estimada de capacidad */}
                <td className="py-3.5 px-3.5 text-center whitespace-nowrap">
                  <AdvisorCapacityUtilizationBadge
                    percent={advisor.workload.capacityUtilizationPercent}
                  />
                </td>

                {/* Fecha de ingreso */}
                <td className="py-3.5 px-3.5 text-right whitespace-nowrap text-slate-400">
                  {formatColombiaDate(advisor.joinedAt)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
