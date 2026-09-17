import type { Lead } from '../types/lead'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { BrainCircuit, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { ScoreIndicator } from './ScoreIndicator'
import { PriorityBadge } from './PriorityBadge'
import { cn } from '@/lib/utils'

export function ScoreExplanationCard({ lead }: { lead: Lead }) {
  const { scoreExplanation } = lead

  return (
    <Card className="border-amber-500/30 bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950">
      <CardHeader className="bg-amber-500/5 border-b border-amber-500/20">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-amber-500/20 flex items-center justify-center text-amber-400">
            <BrainCircuit className="w-4 h-4" />
          </div>
          <div>
            <CardTitle>Explicación del Score y Priorización IA</CardTitle>
            <p className="text-xs text-slate-400 mt-0.5">
              Factores clave detectados por el modelo predictivo
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <PriorityBadge priority={lead.priority} />
          <ScoreIndicator score={lead.score} size="md" />
        </div>
      </CardHeader>

      <CardContent className="space-y-5">
        {/* Resumen ejecutivo */}
        <div className="p-3.5 rounded-lg bg-slate-950/60 border border-slate-800">
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
            Dictamen del Modelo
          </div>
          <p className="text-sm text-slate-200 leading-relaxed font-medium">
            "{scoreExplanation.summary}"
          </p>
          <div className="mt-2.5 flex items-center gap-2 text-xs text-slate-400">
            <span>Confianza del modelo:</span>
            <span className="text-emerald-400 font-mono font-semibold">
              {(scoreExplanation.confidence * 100).toFixed(0)}%
            </span>
          </div>
        </div>

        {/* Lista de factores influyentes */}
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
            Variables de Mayor Impacto (Drivers)
          </h4>
          <div className="space-y-2.5">
            {scoreExplanation.keyDrivers.map((driver) => {
              const isPositive = driver.impact === 'POSITIVO'
              const isNegative = driver.impact === 'NEGATIVO'

              return (
                <div
                  key={driver.id}
                  className="p-3 rounded-lg bg-slate-950/40 border border-slate-800/80 flex items-start justify-between gap-3"
                >
                  <div className="flex items-start gap-2.5">
                    <div
                      className={cn(
                        'w-6 h-6 rounded-md flex items-center justify-center shrink-0 mt-0.5',
                        isPositive && 'bg-emerald-950 text-emerald-400 border border-emerald-800/50',
                        isNegative && 'bg-rose-950 text-rose-400 border border-rose-800/50',
                        !isPositive && !isNegative && 'bg-slate-800 text-slate-400 border border-slate-700'
                      )}
                    >
                      {isPositive && <TrendingUp className="w-3.5 h-3.5" />}
                      {isNegative && <TrendingDown className="w-3.5 h-3.5" />}
                      {!isPositive && !isNegative && <Minus className="w-3.5 h-3.5" />}
                    </div>
                    <div>
                      <div className="text-xs font-semibold text-slate-200">
                        {driver.factor}
                      </div>
                      <p className="text-xs text-slate-400 mt-0.5">
                        {driver.explanation}
                      </p>
                    </div>
                  </div>

                  <div
                    className={cn(
                      'text-xs font-bold font-mono px-2 py-0.5 rounded shrink-0',
                      driver.points > 0 && 'text-emerald-400 bg-emerald-950/60',
                      driver.points < 0 && 'text-rose-400 bg-rose-950/60',
                      driver.points === 0 && 'text-slate-400 bg-slate-800'
                    )}
                  >
                    {driver.points > 0 ? `+${driver.points}` : driver.points} pts
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
