import type { LeadPriority } from '../lead.types'
import { Flame, AlertCircle, Clock } from 'lucide-react'

interface LeadPriorityBadgeProps {
  priority: LeadPriority
}

export function LeadPriorityBadge({ priority }: LeadPriorityBadgeProps) {
  switch (priority) {
    case 'high':
      return (
        <span
          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold bg-rose-950/70 text-rose-300 border border-rose-800/60"
          aria-label="Prioridad Alta"
        >
          <Flame className="w-3.5 h-3.5 text-rose-400" aria-hidden="true" />
          Alta
        </span>
      )
    case 'medium':
      return (
        <span
          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold bg-amber-950/70 text-amber-300 border border-amber-800/60"
          aria-label="Prioridad Media"
        >
          <AlertCircle className="w-3.5 h-3.5 text-amber-400" aria-hidden="true" />
          Media
        </span>
      )
    case 'low':
      return (
        <span
          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-800/80 text-slate-300 border border-slate-700/60"
          aria-label="Prioridad Baja"
        >
          <Clock className="w-3.5 h-3.5 text-slate-400" aria-hidden="true" />
          Baja
        </span>
      )
  }
}
