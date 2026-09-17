import { Link } from 'react-router-dom'
import type { Lead } from '../types/lead'
import { PriorityBadge } from './PriorityBadge'
import { StatusBadge, ChannelBadge } from './StatusBadge'
import { ScoreIndicator } from './ScoreIndicator'
import { formatCurrency, formatRelativeTime } from '@/lib/utils'
import { ArrowRight, User, Bike } from 'lucide-react'

export function LeadsTable({ leads }: { leads: Lead[] }) {
  return (
    <div className="bg-slate-900/70 border border-slate-800/80 rounded-xl overflow-hidden shadow-lg shadow-black/20">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-950/40 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              <th className="py-3.5 px-4">Lead / Cliente</th>
              <th className="py-3.5 px-4">Modelo de Interés</th>
              <th className="py-3.5 px-4">Canal</th>
              <th className="py-3.5 px-4">Prioridad</th>
              <th className="py-3.5 px-4">Score IA</th>
              <th className="py-3.5 px-4">Estado</th>
              <th className="py-3.5 px-4">Última Actividad</th>
              <th className="py-3.5 px-4 text-right">Acción</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-sm">
            {leads.map((lead) => (
              <tr
                key={lead.id}
                className="hover:bg-slate-800/40 transition-colors group cursor-pointer"
              >
                {/* Cliente */}
                <td className="py-3.5 px-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
                      <User className="w-4 h-4" />
                    </div>
                    <div>
                      <Link
                        to={`/leads/${lead.id}`}
                        className="font-semibold text-slate-100 hover:text-amber-400 transition-colors block"
                      >
                        {lead.fullName}
                      </Link>
                      <div className="text-xs text-slate-400 font-mono">
                        {lead.phone}
                      </div>
                    </div>
                  </div>
                </td>

                {/* Modelo de interés */}
                <td className="py-3.5 px-4">
                  <div className="flex items-center gap-1.5 text-slate-200 font-medium">
                    <Bike className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                    <span>{lead.modelOfInterest}</span>
                  </div>
                  {lead.modelPrice && (
                    <div className="text-xs text-slate-400">
                      {formatCurrency(lead.modelPrice)}
                    </div>
                  )}
                </td>

                {/* Canal */}
                <td className="py-3.5 px-4">
                  <ChannelBadge channel={lead.channel} />
                </td>

                {/* Prioridad */}
                <td className="py-3.5 px-4">
                  <PriorityBadge priority={lead.priority} />
                </td>

                {/* Score */}
                <td className="py-3.5 px-4">
                  <ScoreIndicator score={lead.score} />
                </td>

                {/* Estado */}
                <td className="py-3.5 px-4">
                  <StatusBadge status={lead.status} />
                </td>

                {/* Última Actividad */}
                <td className="py-3.5 px-4 text-xs text-slate-400">
                  {formatRelativeTime(lead.lastInteractionDate)}
                </td>

                {/* Acción */}
                <td className="py-3.5 px-4 text-right">
                  <Link
                    to={`/leads/${lead.id}`}
                    className="inline-flex items-center gap-1 text-xs font-semibold text-amber-400 hover:text-amber-300 bg-amber-500/10 hover:bg-amber-500/20 px-2.5 py-1.5 rounded-lg border border-amber-500/30 transition-colors"
                  >
                    Detalle
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
