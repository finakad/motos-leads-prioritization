import { useParams, Link } from 'react-router-dom'
import { useLeadDetail } from '@/features/leads/hooks/useLeads'
import { ScoreExplanationCard } from '@/features/leads/components/ScoreExplanationCard'
import { CommercialSignalsList } from '@/features/leads/components/CommercialSignalsList'
import { ConversationViewer } from '@/features/leads/components/ConversationViewer'
import { PriorityBadge } from '@/features/leads/components/PriorityBadge'
import { StatusBadge, ChannelBadge } from '@/features/leads/components/StatusBadge'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Loader } from '@/components/ui/Loader'
import { ErrorState } from '@/components/ui/ErrorState'
import { formatCurrency, formatDate } from '@/lib/utils'
import {
  ArrowLeft,
  Phone,
  Mail,
  Store,
  Calendar,
  UserCheck,
  Bike,
  ExternalLink,
} from 'lucide-react'

export function LeadDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data: lead, isLoading, isError, error, refetch } = useLeadDetail(id)

  if (isLoading) {
    return (
      <div className="py-20">
        <Loader label="Cargando perfil comercial y diagnóstico del lead..." />
      </div>
    )
  }

  if (isError || !lead) {
    return (
      <div className="py-12 space-y-4">
        <Link to="/leads">
          <Button variant="ghost" size="sm" className="gap-1.5 text-slate-400 mb-2">
            <ArrowLeft className="w-4 h-4" />
            Volver al listado
          </Button>
        </Link>
        <ErrorState
          title="Lead no encontrado o inaccesible"
          message={error instanceof Error ? error.message : 'No se pudo cargar la información del lead.'}
          onRetry={() => refetch()}
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Top navigation & identity */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="space-y-2">
          <Link
            to="/leads"
            className="inline-flex items-center gap-1 text-xs font-semibold text-slate-400 hover:text-amber-400 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Volver a leads priorizados
          </Link>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-bold text-slate-100 tracking-tight">
              {lead.fullName}
            </h1>
            <PriorityBadge priority={lead.priority} />
            <StatusBadge status={lead.status} />
            <ChannelBadge channel={lead.channel} />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <a
            href={`tel:${lead.phone}`}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-sm font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
          >
            <Phone className="w-4 h-4 text-emerald-400" />
            Llamar
          </a>
          <a
            href={`https://wa.me/${lead.phone.replace(/[^0-9]/g, '')}`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-sm font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm shadow-emerald-600/20 transition-colors"
          >
            <ExternalLink className="w-4 h-4" />
            Abrir WhatsApp
          </a>
        </div>
      </div>

      {/* Grid Layout: Information & Diagnostics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Client & Motorcycle info */}
        <div className="space-y-6 lg:col-span-1">
          {/* Card: Datos de Contacto */}
          <Card>
            <CardHeader>
              <CardTitle>Información del Prospecto</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3.5 text-xs">
              <div className="flex items-start gap-2.5">
                <Phone className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
                <div>
                  <span className="text-slate-400 block text-[11px]">Teléfono</span>
                  <span className="text-slate-200 font-mono font-medium">{lead.phone}</span>
                </div>
              </div>

              {lead.email && (
                <div className="flex items-start gap-2.5">
                  <Mail className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
                  <div>
                    <span className="text-slate-400 block text-[11px]">Correo Electrónico</span>
                    <span className="text-slate-200 font-medium">{lead.email}</span>
                  </div>
                </div>
              )}

              <div className="flex items-start gap-2.5">
                <Store className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
                <div>
                  <span className="text-slate-400 block text-[11px]">Punto de Venta / Sede</span>
                  <span className="text-slate-200 font-medium">{lead.storeName}</span>
                </div>
              </div>

              <div className="flex items-start gap-2.5">
                <Calendar className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
                <div>
                  <span className="text-slate-400 block text-[11px]">Fecha de Registro</span>
                  <span className="text-slate-200 font-medium">{formatDate(lead.registrationDate)}</span>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-800 flex items-start gap-2.5">
                <UserCheck className="w-4 h-4 text-amber-400 mt-0.5 shrink-0" />
                <div>
                  <span className="text-slate-400 block text-[11px]">Asesor Asignado</span>
                  <span className="text-slate-200 font-medium">
                    {lead.assignedAdvisor ? lead.assignedAdvisor.name : 'Sin asignar'}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Card: Moto de Interés */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Bike className="w-4 h-4 text-amber-400" />
                <CardTitle>Vehículo de Interés</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <span className="text-[11px] uppercase tracking-wider font-semibold text-slate-400">
                  Modelo Seleccionado
                </span>
                <div className="text-base font-bold text-slate-100 mt-0.5">
                  {lead.modelOfInterest}
                </div>
              </div>

              {lead.modelPrice && (
                <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                  <span className="text-[10px] uppercase font-semibold text-slate-400">
                    Precio de Lista Estimado
                  </span>
                  <div className="text-lg font-bold text-amber-400 font-mono">
                    {formatCurrency(lead.modelPrice)}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Card: Señales Comerciales */}
          <CommercialSignalsList signals={lead.commercialSignals} />
        </div>

        {/* Right Column: Score Breakdown and Conversations */}
        <div className="space-y-6 lg:col-span-2">
          {/* Explicación del Score */}
          <ScoreExplanationCard lead={lead} />

          {/* Historial de Conversación */}
          <ConversationViewer messages={lead.recentMessages} />
        </div>
      </div>
    </div>
  )
}
