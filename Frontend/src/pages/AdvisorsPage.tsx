import { PlaceholderPage } from '@/components/ui/PlaceholderPage'
import { Users } from 'lucide-react'

export function AdvisorsPage() {
  return (
    <PlaceholderPage
      moduleName="Módulo de Equipo Comercial"
      title="Asesores Comerciales"
      description="Espacio reservado para la gestión de fuerza de ventas, asignación de prospectos y métricas de asesor."
      routePath="/advisors"
      icon={<Users className="w-6 h-6 text-emerald-400" />}
    />
  )
}
