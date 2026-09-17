import { Link } from 'react-router-dom'
import { PlaceholderPage } from '@/components/ui/PlaceholderPage'
import { Button } from '@/components/ui/Button'
import { Flame, ArrowRight } from 'lucide-react'

export function LeadsPage() {
  return (
    <PlaceholderPage
      moduleName="Módulo de Prospección"
      title="Leads Priorizados"
      description="Espacio reservado para el listado ordenado predictivamente por score de IA y canales de venta."
      routePath="/leads"
      icon={<Flame className="w-6 h-6 text-amber-500" />}
    >
      <div className="pt-2">
        <span className="text-xs font-semibold text-slate-300 block mb-2">
          Enlaces de prueba a rutas dinámicas de detalle:
        </span>
        <div className="flex flex-wrap gap-2">
          <Link to="/leads/lead-001">
            <Button variant="secondary" size="sm" className="gap-1 text-xs">
              Ver detalle de lead #lead-001
              <ArrowRight className="w-3.5 h-3.5" />
            </Button>
          </Link>
          <Link to="/leads/lead-002">
            <Button variant="secondary" size="sm" className="gap-1 text-xs">
              Ver detalle de lead #lead-002
              <ArrowRight className="w-3.5 h-3.5" />
            </Button>
          </Link>
        </div>
      </div>
    </PlaceholderPage>
  )
}
