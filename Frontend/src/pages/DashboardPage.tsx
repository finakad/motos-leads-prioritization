import { PlaceholderPage } from '@/components/ui/PlaceholderPage'
import { LayoutDashboard } from 'lucide-react'

export function DashboardPage() {
  return (
    <PlaceholderPage
      moduleName="Módulo de Analítica"
      title="Dashboard de Métricas"
      description="Espacio reservado para KPIs comerciales, tasas de conversión y distribución de prospectos."
      routePath="/dashboard"
      icon={<LayoutDashboard className="w-6 h-6 text-cyan-400" />}
    />
  )
}
