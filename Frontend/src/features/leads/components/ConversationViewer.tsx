import type { ConversationMessage } from '../types/lead'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { MessageSquare, Bot, User, Headset } from 'lucide-react'
import { formatRelativeTime } from '@/lib/utils'
import { cn } from '@/lib/utils'

export function ConversationViewer({ messages }: { messages?: ConversationMessage[] }) {
  const getSenderBadge = (sender: ConversationMessage['sender']) => {
    switch (sender) {
      case 'LEAD':
        return {
          label: 'Cliente',
          icon: <User className="w-3 h-3" />,
          color: 'text-slate-300 bg-slate-800 border-slate-700',
        }
      case 'BOT':
        return {
          label: 'Asistente IA',
          icon: <Bot className="w-3 h-3" />,
          color: 'text-amber-400 bg-amber-950/60 border-amber-800/50',
        }
      case 'ASESOR':
        return {
          label: 'Asesor Humano',
          icon: <Headset className="w-3 h-3" />,
          color: 'text-cyan-400 bg-cyan-950/60 border-cyan-800/50',
        }
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-cyan-400" />
          <CardTitle>Historial de Conversación Reciente</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {!messages || messages.length === 0 ? (
          <p className="text-xs text-slate-400 italic">No hay mensajes registrados aún.</p>
        ) : (
          messages.map((msg) => {
            const isLead = msg.sender === 'LEAD'
            const senderConfig = getSenderBadge(msg.sender)

            return (
              <div
                key={msg.id}
                className={cn(
                  'p-3.5 rounded-xl border text-xs space-y-1.5',
                  isLead
                    ? 'bg-slate-900/60 border-slate-800 ml-0 mr-6'
                    : 'bg-slate-850/60 border-amber-900/30 ml-6 mr-0'
                )}
              >
                <div className="flex items-center justify-between">
                  <span
                    className={cn(
                      'inline-flex items-center gap-1 text-[10px] font-bold px-1.5 py-0.5 rounded border',
                      senderConfig.color
                    )}
                  >
                    {senderConfig.icon}
                    {senderConfig.label}
                  </span>
                  <span className="text-[10px] text-slate-400">
                    {formatRelativeTime(msg.timestamp)}
                  </span>
                </div>
                <p className="text-slate-200 leading-relaxed text-[13px]">{msg.message}</p>
              </div>
            )
          })
        )}
      </CardContent>
    </Card>
  )
}
