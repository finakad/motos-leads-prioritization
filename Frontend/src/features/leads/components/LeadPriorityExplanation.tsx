import type { ScoreFactor } from '../lead.types'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { HelpCircle, TrendingUp, Minus, TrendingDown, Info } from 'lucide-react'
import { env } from '@/config/env'

interface LeadPriorityExplanationProps {
  scoreExplanation: string | null
  scoreFactors: ScoreFactor[]
}

export function LeadPriorityExplanation({
  scoreExplanation,
  scoreFactors,
}: LeadPriorityExplanationProps) {
  const renderImpactBadge = (impact: ScoreFactor['impact']) => {
    switch (impact) {
      case 'positive':
        return (
          <span
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-950/70 text-emerald-300 border border-emerald-800/60"
            aria-label="Impacto positivo"
          >
            <TrendingUp className="w-3.5 h-3.5 text-emerald-400" aria-hidden="true" />
            <span>Impacto positivo</span>
          </span>
        )
      case 'negative':
        return (
          <span
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-950/70 text-rose-300 border border-rose-800/60"
            aria-label="Impacto negativo"
          >
            <TrendingDown className="w-3.5 h-3.5 text-rose-400" aria-hidden="true" />
            <span>Impacto negativo</span>
          </span>
        )
      case 'neutral':
      default:
        return (
          <span
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-800 text-slate-300 border border-slate-700/60"
            aria-label="Impacto neutral"
          >
            <Minus className="w-3.5 h-3.5 text-slate-400" aria-hidden="true" />
            <span>Impacto neutral</span>
          </span>
        )
    }
  }

  return (
    <Card className="bg-slate-900/80 border-slate-800">
      <CardHeader className="pb-3 border-b border-slate-800/80">
        <CardTitle className="text-base font-semibold text-slate-100 flex items-center gap-2">
          <HelpCircle className="w-4 h-4 text-amber-400" aria-hidden="true" />
          ¿Por qué se prioriza?
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-4 space-y-4">
        {/* Aviso visible según origen de datos */}
        {env.dataSource === 'api' ? (
          <div className="flex items-start gap-2.5 p-3 rounded-lg bg-emerald-950/30 border border-emerald-800/40 text-xs text-emerald-200">
            <Info className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" aria-hidden="true" />
            <span>
              {scoreFactors.length > 0
                ? 'Explicabilidad calculada por el motor de scoring de FastAPI, evaluando señales conversacionales, calibración histórica, inventario y agilidad de contacto.'
                : 'Detalle de factores pendiente o no disponible para este prospecto en el servicio de scoring.'}
            </span>
          </div>
        ) : (
          <div className="flex items-start gap-2.5 p-3 rounded-lg bg-amber-950/30 border border-amber-800/40 text-xs text-amber-200">
            <Info className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" aria-hidden="true" />
            <span>
              Datos de demostración. La explicación será suministrada por el servicio de priorización.
            </span>
          </div>
        )}

        {/* Texto explicativo del score */}
        <div className="p-3.5 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block mb-1">
            Diagnóstico de prioridad
          </span>
          <p className="text-slate-200 leading-relaxed">
            {scoreExplanation ?? 'No disponible'}
          </p>
        </div>

        {/* Lista de factores influyentes */}
        {scoreFactors.length > 0 && (
          <div className="space-y-2.5 pt-1">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Factores considerados
            </h3>
            <ul className="space-y-2" aria-label="Lista de factores de priorización">
              {scoreFactors.map((factor, index) => (
                <li
                  key={index}
                  className="p-3 rounded-lg bg-slate-950/40 border border-slate-800/70 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5"
                >
                  <div className="space-y-0.5">
                    <div className="text-xs font-semibold text-slate-100">
                      {factor.label}
                    </div>
                    <p className="text-xs text-slate-400">
                      {factor.description}
                    </p>
                  </div>
                  <div className="shrink-0">
                    {renderImpactBadge(factor.impact)}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
