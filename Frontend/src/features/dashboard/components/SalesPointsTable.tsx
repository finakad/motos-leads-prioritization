import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import type { SalesPointKpiRow } from '../dashboard.types'
import { Store } from 'lucide-react'

interface SalesPointsTableProps {
  salesPoints: SalesPointKpiRow[]
}

export function SalesPointsTable({ salesPoints }: SalesPointsTableProps) {
  return (
    <Card className="border-slate-800/80 bg-slate-900/60">
      <CardHeader className="pb-3 border-b border-slate-800/60">
        <CardTitle className="text-sm font-semibold text-slate-200 flex items-center gap-2">
          <Store className="w-4 h-4 text-cyan-400" />
          Rendimiento por Punto de Venta / Sede
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 font-semibold border-b border-slate-800/60 uppercase tracking-wider">
              <tr>
                <th className="px-4 py-3">Punto de Venta</th>
                <th className="px-4 py-3 text-center">Total Leads</th>
                <th className="px-4 py-3 text-center">Alta Prioridad</th>
                <th className="px-4 py-3 text-center">% Alta</th>
                <th className="px-4 py-3 text-right">Score Promedio</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/40 text-slate-300">
              {salesPoints.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-6 text-center text-slate-500">
                    No se registraron puntos de venta con actividad.
                  </td>
                </tr>
              ) : (
                salesPoints.map((row) => {
                  const pct =
                    row.totalLeads > 0
                      ? Math.round((row.highPriorityLeads / row.totalLeads) * 1000) / 10
                      : 0

                  return (
                    <tr key={row.salesPointId} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-4 py-3 font-semibold text-slate-100 flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-cyan-400" />
                        {row.salesPointId}
                      </td>
                      <td className="px-4 py-3 text-center font-mono font-medium">
                        {row.totalLeads}
                      </td>
                      <td className="px-4 py-3 text-center font-mono font-bold text-rose-400">
                        {row.highPriorityLeads}
                      </td>
                      <td className="px-4 py-3 text-center font-mono">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[11px] font-semibold ${
                            pct >= 35
                              ? 'bg-rose-950/60 text-rose-300 border border-rose-800/40'
                              : 'bg-slate-800 text-slate-300'
                          }`}
                        >
                          {pct}%
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right font-mono font-bold text-emerald-400">
                        {row.averageScore !== null ? `${row.averageScore} pts` : 'N/D'}
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}
