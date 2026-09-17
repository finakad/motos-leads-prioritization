import type { LeadConversation } from '../lead.types'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { formatColombiaDate } from '@/lib/utils'
import { MessageSquare, User, Headset, Bot, Inbox } from 'lucide-react'

interface LeadConversationsSectionProps {
  conversations: LeadConversation[]
}

export function LeadConversationsSection({
  conversations,
}: LeadConversationsSectionProps) {
  const getSenderConfig = (sender: string) => {
    const s = sender.toLowerCase()
    if (s.includes('cliente')) {
      return {
        roleLabel: 'Cliente',
        icon: <User className="w-3.5 h-3.5" aria-hidden="true" />,
        badgeClass: 'bg-slate-800 text-slate-200 border-slate-700',
        containerClass: 'bg-slate-950/60 border-slate-800 ml-0 mr-4 sm:mr-8',
      }
    }
    if (s.includes('asesor')) {
      return {
        roleLabel: 'Asesor Comercial',
        icon: <Headset className="w-3.5 h-3.5 text-cyan-400" aria-hidden="true" />,
        badgeClass: 'bg-cyan-950/80 text-cyan-300 border-cyan-800/60',
        containerClass: 'bg-slate-900/90 border-cyan-950/50 ml-4 sm:ml-8 mr-0',
      }
    }
    return {
      roleLabel: sender,
      icon: <Bot className="w-3.5 h-3.5 text-amber-400" aria-hidden="true" />,
      badgeClass: 'bg-amber-950/80 text-amber-300 border-amber-800/60',
      containerClass: 'bg-slate-950/40 border-slate-800 ml-2 mr-2',
    }
  }

  return (
    <Card className="bg-slate-900/80 border-slate-800">
      <CardHeader className="pb-3 border-b border-slate-800/80">
        <CardTitle className="text-base font-semibold text-slate-100 flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-emerald-400" aria-hidden="true" />
          Conversaciones
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-4 space-y-6">
        {/* Si no hay conversaciones */}
        {conversations.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-8 text-center rounded-lg border border-dashed border-slate-800 bg-slate-950/30">
            <Inbox className="w-8 h-8 text-slate-500 mb-2" aria-hidden="true" />
            <p className="text-xs font-semibold text-slate-300">
              No hay conversaciones registradas
            </p>
            <p className="text-xs text-slate-500 mt-0.5">
              Este prospecto aún no cuenta con historial de mensajes o interacciones registradas.
            </p>
          </div>
        ) : (
          conversations.map((conv) => (
            <div key={conv.id} className="space-y-3">
              {/* Encabezado de la conversación */}
              <div className="flex flex-wrap items-center justify-between gap-2 px-3 py-2 rounded-lg bg-slate-950/60 border border-slate-800 text-xs">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-slate-200">Canal:</span>
                  <span className="text-slate-300">{conv.channel}</span>
                </div>
                <div className="flex items-center gap-1.5 text-slate-400 font-mono">
                  <span>Iniciada:</span>
                  <span>{formatColombiaDate(conv.startedAt)}</span>
                </div>
              </div>

              {/* Mensajes en orden cronológico */}
              <ol className="space-y-2.5 list-none p-0 m-0" aria-label="Historial de mensajes">
                {conv.messages.map((msg) => {
                  const senderConfig = getSenderConfig(msg.sender)

                  return (
                    <li
                      key={msg.id}
                      className={`p-3 rounded-lg border text-xs space-y-1.5 transition-colors ${senderConfig.containerClass}`}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold border ${senderConfig.badgeClass}`}
                        >
                          {senderConfig.icon}
                          <span>{senderConfig.roleLabel}</span>
                        </span>
                        <time
                          dateTime={msg.sentAt}
                          className="text-[11px] text-slate-400 font-mono"
                        >
                          {formatColombiaDate(msg.sentAt)}
                        </time>
                      </div>
                      <p className="text-slate-200 text-xs leading-relaxed">
                        {msg.text}
                      </p>
                    </li>
                  )
                })}
              </ol>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  )
}
