import type { LeadStatus, LeadChannel } from '../types/lead'
import { Badge } from '@/components/ui/Badge'
import { MessageSquare, Globe, Store, Camera, ThumbsUp } from 'lucide-react'

export function StatusBadge({ status }: { status: LeadStatus }) {
  switch (status) {
    case 'NUEVO':
      return <Badge variant="info">Nuevo</Badge>
    case 'CONTACTADO':
      return <Badge variant="warning">Contactado</Badge>
    case 'EN_GESTION':
      return <Badge variant="default">En Gestión</Badge>
    case 'CALIFICADO':
      return <Badge variant="success">Calificado</Badge>
    case 'DESCARTADO':
      return <Badge variant="neutral">Descartado</Badge>
    case 'VENTA_CERRADA':
      return <Badge variant="success" className="bg-emerald-500/20 text-emerald-300 border-emerald-500/40">Venta Cerrada</Badge>
  }
}

export function ChannelBadge({ channel }: { channel: LeadChannel }) {
  switch (channel) {
    case 'WHATSAPP':
      return (
        <span className="inline-flex items-center gap-1 text-xs font-medium text-emerald-400 bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-800/40">
          <MessageSquare className="w-3 h-3" />
          WhatsApp
        </span>
      )
    case 'WEB':
      return (
        <span className="inline-flex items-center gap-1 text-xs font-medium text-cyan-400 bg-cyan-950/40 px-2 py-0.5 rounded border border-cyan-800/40">
          <Globe className="w-3 h-3" />
          Sitio Web
        </span>
      )
    case 'INSTAGRAM':
      return (
        <span className="inline-flex items-center gap-1 text-xs font-medium text-pink-400 bg-pink-950/40 px-2 py-0.5 rounded border border-pink-800/40">
          <Camera className="w-3 h-3" />
          Instagram
        </span>
      )
    case 'FACEBOOK':
      return (
        <span className="inline-flex items-center gap-1 text-xs font-medium text-blue-400 bg-blue-950/40 px-2 py-0.5 rounded border border-blue-800/40">
          <ThumbsUp className="w-3 h-3" />
          Facebook
        </span>
      )
    case 'CONCESIONARIO':
      return (
        <span className="inline-flex items-center gap-1 text-xs font-medium text-amber-400 bg-amber-950/40 px-2 py-0.5 rounded border border-amber-800/40">
          <Store className="w-3 h-3" />
          Concesionario
        </span>
      )
  }
}
