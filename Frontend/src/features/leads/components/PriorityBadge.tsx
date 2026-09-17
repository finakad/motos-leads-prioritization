import type { LeadPriority } from '../types/lead'
import { Badge } from '@/components/ui/Badge'
import { Flame, AlertCircle, Clock } from 'lucide-react'

export function PriorityBadge({ priority }: { priority: LeadPriority }) {
  switch (priority) {
    case 'ALTA':
      return (
        <Badge variant="danger" size="md" className="gap-1 shadow-sm shadow-rose-950/40">
          <Flame className="w-3.5 h-3.5 text-rose-400 fill-rose-500/30" />
          Prioridad Alta
        </Badge>
      )
    case 'MEDIA':
      return (
        <Badge variant="warning" size="md" className="gap-1">
          <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
          Prioridad Media
        </Badge>
      )
    case 'BAJA':
      return (
        <Badge variant="neutral" size="md" className="gap-1">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          Prioridad Baja
        </Badge>
      )
  }
}
