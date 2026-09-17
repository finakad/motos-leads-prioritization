import { useParams, Link } from 'react-router-dom'
import { useLeadDetail } from '@/features/leads/hooks/use-lead-detail'
import { LeadPriorityBadge } from '@/features/leads/components/LeadPriorityBadge'
import { LeadScoreBadge } from '@/features/leads/components/LeadScoreBadge'
import { LeadCommercialSummary } from '@/features/leads/components/LeadCommercialSummary'
import { LeadPriorityExplanation } from '@/features/leads/components/LeadPriorityExplanation'
import { LeadConversationsSection } from '@/features/leads/components/LeadConversationsSection'
import { Loader } from '@/components/ui/Loader'
import { ErrorState } from '@/components/ui/ErrorState'
import { Button } from '@/components/ui/Button'
import { ArrowLeft, User, SearchX } from 'lucide-react'

export function LeadDetailPage() {
  const { leadId } = useParams<{ leadId: string }>()
  const { data: lead, isLoading, isError, error, refetch } = useLeadDetail(leadId)

  // Estado: Carga
  if (isLoading) {
    return (
      <div className="py-24">
        <Loader label="Cargando información detallada del prospecto..." />
      </div>
    )
  }

  // Estado: Error de consulta
  if (isError) {
    return (
      <div className="space-y-4 max-w-xl mx-auto py-12">
        <Link to="/leads">
          <Button variant="ghost" size="sm" className="gap-1.5 text-xs text-slate-400">
            <ArrowLeft className="w-3.5 h-3.5" aria-hidden="true" />
            Volver a leads
          </Button>
        </Link>
        <ErrorState
          title="Error al cargar el detalle del lead"
          message={error instanceof Error ? error.message : 'Ocurrió un error inesperado al consultar los datos.'}
          onRetry={() => refetch()}
        />
      </div>
    )
  }

  // Estado: Lead no encontrado
  if (!lead) {
    return (
      <div className="space-y-6 max-w-md mx-auto py-16 text-center">
        <div className="w-14 h-14 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-amber-400 mx-auto">
          <SearchX className="w-7 h-7" aria-hidden="true" />
        </div>
        <div className="space-y-2">
          <h1 className="text-xl font-bold text-slate-100">Lead no encontrado</h1>
          <p className="text-xs text-slate-400 leading-relaxed">
            El identificador <strong className="text-slate-200 font-mono">"{leadId}"</strong> no existe en los datos de demostración de la plataforma.
          </p>
        </div>
        <Link to="/leads" className="inline-block pt-2">
          <Button variant="primary" size="sm" className="gap-2">
            <ArrowLeft className="w-4 h-4" aria-hidden="true" />
            Volver a leads
          </Button>
        </Link>
      </div>
    )
  }

  // Estado: Detalle disponible
  return (
    <div className="space-y-6">
      {/* 1. Encabezado */}
      <header className="space-y-3 border-b border-slate-800/80 pb-5">
        <nav aria-label="Navegación de retorno">
          <Link
            to="/leads"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-amber-400 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" aria-hidden="true" />
            <span>Volver a leads</span>
          </Link>
        </nav>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shrink-0">
              <User className="w-5 h-5" aria-hidden="true" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-100 tracking-tight">
                {lead.customerName}
              </h1>
              <div className="text-xs text-slate-400 font-mono mt-0.5">
                Identificador: <span className="text-slate-200 font-semibold">{lead.id}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3 self-start sm:self-auto">
            <LeadPriorityBadge priority={lead.priority} />
            <LeadScoreBadge score={lead.score} />
          </div>
        </div>
      </header>

      {/* 2. Resumen Comercial */}
      <section aria-labelledby="resumen-comercial-title">
        <LeadCommercialSummary lead={lead} />
      </section>

      {/* 3. Explicación de Prioridad */}
      <section aria-labelledby="prioridad-explicacion-title">
        <LeadPriorityExplanation
          scoreExplanation={lead.scoreExplanation}
          scoreFactors={lead.scoreFactors}
        />
      </section>

      {/* 4. Conversaciones */}
      <section aria-labelledby="conversaciones-title">
        <LeadConversationsSection conversations={lead.conversations} />
      </section>
    </div>
  )
}
