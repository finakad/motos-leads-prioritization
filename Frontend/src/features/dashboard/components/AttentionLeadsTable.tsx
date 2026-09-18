import { Link } from 'react-router-dom'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import type { AttentionLeadItem } from '../dashboard.types'
import { Flame, ArrowUpRight, Phone, Bike } from 'lucide-react'

interface AttentionLeadsTableProps {
  leads: AttentionLeadItem[]
}

export function AttentionLeadsTable({ leads }: AttentionLeadsTableProps) {
  return (
    <Card className="border-slate-800/80 bg-slate-900/60">
      <CardHeader className="pb-3 border-b border-slate-800/60 flex items-center justify-between">
        <CardTitle className="text-sm font-semibold text-slate-200 flex items-center gap-2">
          <Flame className="w-4 h-4 text-rose-500" />
          Top 5 Leads de Atención Inmediata (Mayor Score)
        </CardTitle>
        <Link
          to="/leads"
          className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 flex items-center gap-1 transition-colors"
        >
          Ver todos los leads
          <ArrowUpRight className="w-3.5 h-3.5" />
        </Link>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 font-semibold border-b border-slate-800/60 uppercase tracking-wider">
              <tr>
                <th className="px-4 py-3">Cliente</th>
                <th className="px-4 py-3">Sede / Canal</th>
                <th className="px-4 py-3">Modelo Interés</th>
                <th className="px-4 py-3 text-center">Score</th>
                <th className="px-4 py-3 text-center">Prioridad</th>
                <th className="px-4 py-3 text-right">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/40 text-slate-300">
              {leads.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-6 text-center text-slate-500">
                    No hay leads con score calculado para mostrar.
                  </td>
                </tr>
              ) : (
                leads.map((lead) => (
                  <tr key={lead.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-4 py-3">
                      <div className="font-semibold text-slate-100">{lead.customerName}</div>
                      <div className="text-[11px] text-slate-400 flex items-center gap-1 mt-0.5">
                        <Phone className="w-3 h-3 text-slate-500" />
                        {lead.phoneMasked}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="font-medium text-slate-200">{lead.salesPointId}</div>
                      <div className="text-[11px] text-slate-400">{lead.channel}</div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1 text-slate-200 font-medium">
                        <Bike className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                        <span className="truncate max-w-[140px]" title={lead.modelInterest}>
                          {lead.modelInterest}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-center font-mono font-bold text-sm text-emerald-400">
                      {lead.score !== null ? Math.round(lead.score * 10) / 10 : 'N/D'}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <Badge
                        variant={
                          lead.priorityTier === 'ALTA'
                            ? 'danger'
                            : lead.priorityTier === 'MEDIA'
                            ? 'warning'
                            : 'neutral'
                        }
                        size="sm"
                      >
                        {lead.priorityTier || 'PENDIENTE'}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Link
                        to={`/leads/${lead.id}`}
                        className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 transition-colors"
                      >
                        Ver Detalle
                        <ArrowUpRight className="w-3 h-3" />
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}
