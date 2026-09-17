import { useParams, Link } from 'react-router-dom'
import { PlaceholderPage } from '@/components/ui/PlaceholderPage'
import { Button } from '@/components/ui/Button'
import { UserCheck, ArrowLeft } from 'lucide-react'

export function LeadDetailPage() {
  const { leadId } = useParams<{ leadId: string }>()

  return (
    <PlaceholderPage
      moduleName="Módulo de Detalle"
      title={`Detalle del Lead: ${leadId ?? 'Sin Identificador'}`}
      description="Espacio reservado para el perfil comercial, diagnóstico del modelo predictivo, historial de chat y señales."
      routePath={`/leads/${leadId ?? ':leadId'}`}
      icon={<UserCheck className="w-6 h-6 text-emerald-400" />}
    >
      <div className="pt-2">
        <Link to="/leads">
          <Button variant="outline" size="sm" className="gap-1.5 text-xs text-slate-300">
            <ArrowLeft className="w-3.5 h-3.5" />
            Volver a la lista de leads
          </Button>
        </Link>
      </div>
    </PlaceholderPage>
  )
}
