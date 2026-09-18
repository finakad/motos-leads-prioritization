import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import type { DashboardDistributions as DistributionsType, DistributionItem } from '../dashboard.types'
import { Flame, MessageSquare, CheckCircle2 } from 'lucide-react'

interface DashboardDistributionsViewProps {
  distributions: DistributionsType
}

function DistributionList({
  items,
  barColor = 'bg-cyan-500',
}: {
  items: DistributionItem[]
  barColor?: string
}) {
  if (items.length === 0) {
    return <p className="text-xs text-slate-500 italic py-2">Sin datos disponibles.</p>
  }

  return (
    <div className="space-y-3">
      {items.map((item) => (
        <div key={item.label} className="space-y-1">
          <div className="flex justify-between items-center text-xs">
            <span className="font-medium text-slate-300">{item.label}</span>
            <span className="text-slate-400 font-mono">
              {item.value} <span className="text-slate-500">({item.percentage}%)</span>
            </span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${barColor}`}
              style={{ width: `${Math.min(100, Math.max(2, item.percentage))}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  )
}

export function DashboardDistributionsView({ distributions }: DashboardDistributionsViewProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {/* Prioridad */}
      <Card className="border-slate-800/80 bg-slate-900/60">
        <CardHeader className="pb-3 border-b border-slate-800/60">
          <CardTitle className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <Flame className="w-4 h-4 text-rose-400" />
            Distribución por Prioridad
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-4">
          <DistributionList items={distributions.priority} barColor="bg-rose-500" />
        </CardContent>
      </Card>

      {/* Canales */}
      <Card className="border-slate-800/80 bg-slate-900/60">
        <CardHeader className="pb-3 border-b border-slate-800/60">
          <CardTitle className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-cyan-400" />
            Canales de Captación
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-4">
          <DistributionList items={distributions.channel} barColor="bg-cyan-500" />
        </CardContent>
      </Card>

      {/* Estado de Gestión */}
      <Card className="border-slate-800/80 bg-slate-900/60">
        <CardHeader className="pb-3 border-b border-slate-800/60">
          <CardTitle className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            Estado de Gestión
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-4">
          <DistributionList items={distributions.managementStatus} barColor="bg-emerald-500" />
        </CardContent>
      </Card>
    </div>
  )
}
