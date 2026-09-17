import { useLeads } from '@/features/leads/hooks/useLeads'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Loader } from '@/components/ui/Loader'
import {
  LayoutDashboard,
  Flame,
  CheckCircle2,
  TrendingUp,
  Percent,
} from 'lucide-react'

export function DashboardPage() {
  const { data, isLoading } = useLeads()
  const leads = data?.data || []

  const totalLeads = leads.length
  const highPriority = leads.filter((l) => l.priority === 'ALTA').length
  const mediumPriority = leads.filter((l) => l.priority === 'MEDIA').length
  const lowPriority = leads.filter((l) => l.priority === 'BAJA').length
  const qualified = leads.filter((l) => l.status === 'CALIFICADO' || l.status === 'VENTA_CERRADA').length

  const highPriorityPercentage = totalLeads > 0 ? Math.round((highPriority / totalLeads) * 100) : 0

  if (isLoading) {
    return (
      <div className="py-20">
        <Loader label="Calculando métricas del panel general..." />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight flex items-center gap-2.5">
          <LayoutDashboard className="w-6 h-6 text-cyan-400" />
          Dashboard de Conversión y Métricas
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Rendimiento del embudo de leads priorizados por inteligencia predictiva.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-5">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase">
            <span>Total Leads Activos</span>
            <TrendingUp className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-3xl font-bold text-slate-100 font-mono mt-2">{totalLeads}</div>
          <div className="text-xs text-slate-400 mt-1">En la sede actual</div>
        </Card>

        <Card className="p-5 border-rose-900/30">
          <div className="flex items-center justify-between text-rose-400 text-xs font-semibold uppercase">
            <span>Prioridad Alta</span>
            <Flame className="w-4 h-4" />
          </div>
          <div className="text-3xl font-bold text-rose-400 font-mono mt-2">{highPriority}</div>
          <div className="text-xs text-slate-400 mt-1">{highPriorityPercentage}% del volumen total</div>
        </Card>

        <Card className="p-5 border-amber-900/30">
          <div className="flex items-center justify-between text-amber-400 text-xs font-semibold uppercase">
            <span>Prioridad Media</span>
            <Percent className="w-4 h-4" />
          </div>
          <div className="text-3xl font-bold text-amber-400 font-mono mt-2">{mediumPriority}</div>
          <div className="text-xs text-slate-400 mt-1">Requieren maduración</div>
        </Card>

        <Card className="p-5 border-emerald-900/30">
          <div className="flex items-center justify-between text-emerald-400 text-xs font-semibold uppercase">
            <span>Calificados / Cerrados</span>
            <CheckCircle2 className="w-4 h-4" />
          </div>
          <div className="text-3xl font-bold text-emerald-400 font-mono mt-2">{qualified}</div>
          <div className="text-xs text-slate-400 mt-1">Con alta probabilidad de venta</div>
        </Card>
      </div>

      {/* Breakdown grids */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Distribución de Prioridades</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-300 font-medium">Alta Prioridad ({highPriority})</span>
                <span className="text-rose-400 font-mono font-semibold">{highPriorityPercentage}%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-rose-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${highPriorityPercentage}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-300 font-medium">Media Prioridad ({mediumPriority})</span>
                <span className="text-amber-400 font-mono font-semibold">
                  {totalLeads > 0 ? Math.round((mediumPriority / totalLeads) * 100) : 0}%
                </span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-amber-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${totalLeads > 0 ? (mediumPriority / totalLeads) * 100 : 0}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-300 font-medium">Baja Prioridad ({lowPriority})</span>
                <span className="text-slate-400 font-mono font-semibold">
                  {totalLeads > 0 ? Math.round((lowPriority / totalLeads) * 100) : 0}%
                </span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-slate-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${totalLeads > 0 ? (lowPriority / totalLeads) * 100 : 0}%` }}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Canales con Mayor Intención de Compra</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950/40 border border-slate-800">
              <span className="font-semibold text-emerald-400">WhatsApp Oficial</span>
              <span className="text-slate-300">Score promedio: <strong className="text-emerald-400 font-mono">94 pts</strong></span>
            </div>
            <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950/40 border border-slate-800">
              <span className="font-semibold text-amber-400">Concesionario Presencial</span>
              <span className="text-slate-300">Score promedio: <strong className="text-emerald-400 font-mono">91 pts</strong></span>
            </div>
            <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950/40 border border-slate-800">
              <span className="font-semibold text-pink-400">Instagram Direct</span>
              <span className="text-slate-300">Score promedio: <strong className="text-amber-400 font-mono">87 pts</strong></span>
            </div>
            <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950/40 border border-slate-800">
              <span className="font-semibold text-cyan-400">Formulario Web</span>
              <span className="text-slate-300">Score promedio: <strong className="text-amber-400 font-mono">55 pts</strong></span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
