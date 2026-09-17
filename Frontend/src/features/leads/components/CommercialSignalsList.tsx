import type { CommercialSignal } from '../types/lead'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Radio, Zap } from 'lucide-react'
import { formatRelativeTime } from '@/lib/utils'

export function CommercialSignalsList({ signals }: { signals: CommercialSignal[] }) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-amber-400" />
          <CardTitle>Señales Comerciales Detectadas</CardTitle>
        </div>
        <span className="text-xs text-slate-400 font-mono">
          {signals.length} {signals.length === 1 ? 'señal' : 'señales'}
        </span>
      </CardHeader>
      <CardContent className="space-y-2.5">
        {signals.length === 0 ? (
          <p className="text-xs text-slate-400 italic">No se han detectado señales adicionales.</p>
        ) : (
          signals.map((sig) => (
            <div
              key={sig.id}
              className="p-3 rounded-lg bg-slate-950/40 border border-slate-800/80 flex items-start gap-2.5"
            >
              <Radio className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-amber-400">
                    {sig.type}
                  </span>
                  <span className="text-[10px] text-slate-400">
                    {formatRelativeTime(sig.detectedAt)}
                  </span>
                </div>
                <p className="text-xs text-slate-200 mt-1">{sig.description}</p>
              </div>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  )
}
