import { Link } from 'react-router-dom'
import type { PrioritizedLead } from '../lead.types'
import { LeadPriorityBadge } from './LeadPriorityBadge'
import { LeadScoreBadge } from './LeadScoreBadge'
import { formatColombiaDate } from '@/lib/utils'
import { ArrowRight } from 'lucide-react'

interface LeadsTableProps {
  leads: PrioritizedLead[]
}

export function LeadsTable({ leads }: LeadsTableProps) {
  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden shadow-lg shadow-black/20">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse min-w-[760px]">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-950/60 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              <th scope="col" className="py-3 px-4">Prioridad</th>
              <th scope="col" className="py-3 px-4">Score</th>
              <th scope="col" className="py-3 px-4">Cliente</th>
              <th scope="col" className="py-3 px-4">Canal</th>
              <th scope="col" className="py-3 px-4">Modelo de interés</th>
              <th scope="col" className="py-3 px-4">Estado de gestión</th>
              <th scope="col" className="py-3 px-4">Punto de venta</th>
              <th scope="col" className="py-3 px-4">Fecha de registro</th>
              <th scope="col" className="py-3 px-4 text-right">Acción</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-xs">
            {leads.map((lead) => (
              <tr
                key={lead.id}
                className="hover:bg-slate-800/40 transition-colors"
              >
                {/* Prioridad */}
                <td className="py-3 px-4 whitespace-nowrap">
                  <LeadPriorityBadge priority={lead.priority} />
                </td>

                {/* Score */}
                <td className="py-3 px-4 whitespace-nowrap">
                  <LeadScoreBadge score={lead.score} />
                </td>

                {/* Cliente */}
                <td className="py-3 px-4">
                  <div className="font-semibold text-slate-100">
                    {lead.customerName}
                  </div>
                  <div className="text-[11px] text-slate-500 font-mono">
                    ID: {lead.id}
                  </div>
                </td>

                {/* Canal */}
                <td className="py-3 px-4 whitespace-nowrap text-slate-300">
                  {lead.channel ?? 'No especificado'}
                </td>

                {/* Modelo de interés */}
                <td className="py-3 px-4 text-slate-200 font-medium">
                  {lead.modelInterestText ?? 'Sin modelo'}
                </td>

                {/* Estado de gestión */}
                <td className="py-3 px-4 whitespace-nowrap">
                  <span className="inline-flex px-2 py-0.5 rounded text-[11px] font-medium bg-slate-800 text-slate-300 border border-slate-700/60">
                    {lead.managementStatus ?? 'Pendiente'}
                  </span>
                </td>

                {/* Punto de venta */}
                <td className="py-3 px-4 whitespace-nowrap font-mono text-slate-400">
                  {lead.salesPointId}
                </td>

                {/* Fecha de registro (formato Colombia America/Bogota) */}
                <td className="py-3 px-4 whitespace-nowrap text-slate-400">
                  {formatColombiaDate(lead.registeredAt)}
                </td>

                {/* Acción */}
                <td className="py-3 px-4 text-right whitespace-nowrap">
                  <Link
                    to={`/leads/${lead.id}?companyId=${lead.companyId}`}
                    className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold text-amber-400 hover:text-amber-300 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 transition-colors focus:outline-none focus:ring-2 focus:ring-amber-500/50"
                  >
                    <span>Ver detalle</span>
                    <ArrowRight className="w-3.5 h-3.5" aria-hidden="true" />
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
