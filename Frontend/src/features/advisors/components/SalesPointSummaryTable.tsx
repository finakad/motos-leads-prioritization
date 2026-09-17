import type { SalesPointSummary } from '../advisor.types'
import { AdvisorCapacityUtilizationBadge } from './AdvisorCapacityUtilizationBadge'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Store, Flame } from 'lucide-react'

interface SalesPointSummaryTableProps {
  summaries: SalesPointSummary[]
}

export function SalesPointSummaryTable({ summaries }: SalesPointSummaryTableProps) {
  if (summaries.length === 0) {
    return null
  }

  return (
    <Card className="bg-slate-900/80 border-slate-800">
      <CardHeader className="pb-3 border-b border-slate-800/80">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold text-slate-100 flex items-center gap-2">
            <Store className="w-4 h-4 text-indigo-400" aria-hidden="true" />
            Resumen de carga operativa por punto de venta
          </CardTitle>
          <span className="text-xs text-slate-400 font-mono">
            {summaries.length} {summaries.length === 1 ? 'sede' : 'sedes'}
          </span>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[780px]">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/40 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                <th scope="col" className="py-3 px-4">Empresa</th>
                <th scope="col" className="py-3 px-4">Punto de venta</th>
                <th scope="col" className="py-3 px-4 text-center">Asesores activos</th>
                <th scope="col" className="py-3 px-4 text-center">Capacidad diaria total</th>
                <th scope="col" className="py-3 px-4 text-center">Total leads</th>
                <th scope="col" className="py-3 px-4 text-center">Alta prioridad</th>
                <th scope="col" className="py-3 px-4 text-center">Carga prom. / asesor</th>
                <th scope="col" className="py-3 px-4 text-center">Utilización estimada</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs">
              {summaries.map((item) => (
                <tr
                  key={`${item.companyId}-${item.salesPointId}`}
                  className="hover:bg-slate-800/40 transition-colors"
                >
                  {/* Empresa */}
                  <td className="py-3 px-4 font-mono font-medium text-slate-300">
                    {item.companyId}
                  </td>

                  {/* Punto de venta */}
                  <td className="py-3 px-4 font-mono font-bold text-slate-100">
                    {item.salesPointId}
                  </td>

                  {/* Asesores activos */}
                  <td className="py-3 px-4 text-center font-mono text-emerald-400 font-semibold">
                    {item.activeAdvisorsCount}
                  </td>

                  {/* Capacidad diaria total */}
                  <td className="py-3 px-4 text-center font-mono text-slate-200">
                    {item.dailyCapacityTotal} leads/día
                  </td>

                  {/* Total leads */}
                  <td className="py-3 px-4 text-center font-mono font-bold text-slate-100">
                    {item.totalLeads}
                  </td>

                  {/* Leads alta prioridad */}
                  <td className="py-3 px-4 text-center whitespace-nowrap">
                    {item.highPriorityLeads > 0 ? (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-rose-950/60 text-rose-400 border border-rose-900/60">
                        <Flame className="w-3 h-3" aria-hidden="true" />
                        {item.highPriorityLeads}
                      </span>
                    ) : (
                      <span className="text-slate-500 font-mono">0</span>
                    )}
                  </td>

                  {/* Carga promedio estimada */}
                  <td className="py-3 px-4 text-center font-mono text-slate-200">
                    {item.estimatedLeadsPerAdvisor > 0
                      ? `~${item.estimatedLeadsPerAdvisor}`
                      : 'No disponible'}
                  </td>

                  {/* Utilización estimada */}
                  <td className="py-3 px-4 text-center whitespace-nowrap">
                    <AdvisorCapacityUtilizationBadge
                      percent={item.capacityUtilizationPercent}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}
