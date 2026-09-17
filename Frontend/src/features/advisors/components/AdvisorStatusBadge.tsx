import type { AdvisorStatus } from '../advisor.types'
import { CheckCircle2, UserX } from 'lucide-react'

interface AdvisorStatusBadgeProps {
  status: AdvisorStatus
}

export function AdvisorStatusBadge({ status }: AdvisorStatusBadgeProps) {
  if (status === 'active') {
    return (
      <span
        className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-semibold bg-emerald-950/70 text-emerald-300 border border-emerald-800/60"
        aria-label="Estado: Activo"
      >
        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" aria-hidden="true" />
        <span>Activo</span>
      </span>
    )
  }

  return (
    <span
      className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700/60"
      aria-label="Estado: Inactivo"
    >
      <UserX className="w-3.5 h-3.5 text-slate-400" aria-hidden="true" />
      <span>Inactivo</span>
    </span>
  )
}
