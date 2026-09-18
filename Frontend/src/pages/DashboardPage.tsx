import { useState } from 'react'
import {
  useDashboard,
  DashboardHeader,
  DashboardKpiCards,
  DashboardDistributionsView,
  SalesPointsTable,
  AttentionLeadsTable,
} from '@/features/dashboard'
import { Loader } from '@/components/ui/Loader'
import { ErrorState } from '@/components/ui/ErrorState'
import { EmptyState } from '@/components/ui/EmptyState'
import { env } from '@/config/env'

export function DashboardPage() {
  const [selectedCompany, setSelectedCompany] = useState<string>(env.defaultCompanyId)

  const {
    data,
    isLoading,
    isError,
    error,
    refetch,
    isRefetching,
  } = useDashboard(selectedCompany)

  return (
    <div className="space-y-6">
      {/* Encabezado y barra de control siempre visible */}
      <DashboardHeader
        selectedCompany={selectedCompany}
        onSelectCompany={(compId) => setSelectedCompany(compId)}
        dataSource={data?.metadata.dataSource ?? env.dataSource}
        isDerived={data?.metadata.isDerived ?? (env.dataSource === 'api')}
        sampleSize={data?.metadata.sampleSize ?? 0}
        totalCompanyLeads={data?.metadata.totalCompanyLeads ?? 0}
        syncTime={data?.metadata.syncTime ?? ''}
        notice={data?.metadata.notice}
        onRefresh={() => void refetch()}
        isRefreshing={isRefetching}
      />

      {/* Estados de Carga, Error, Vacío y Contenido Normal */}
      {isLoading ? (
        <div className="py-20 flex justify-center">
          <Loader label={`Cargando y calculando métricas comerciales para ${selectedCompany}...`} />
        </div>
      ) : isError ? (
        <ErrorState
          title={`Error al consultar métricas de ${selectedCompany}`}
          message={
            error?.message ||
            'No fue posible obtener los leads desde FastAPI para calcular las métricas del dashboard.'
          }
          onRetry={() => void refetch()}
        />
      ) : !data || data.metrics.totalLeads === 0 ? (
        <EmptyState
          title="Sin datos comerciales"
          description={`No se encontraron leads priorizados ni registros históricos para la empresa ${selectedCompany}.`}
        />
      ) : (
        <div className="space-y-6">
          {/* Tarjetas KPI Superiores */}
          <DashboardKpiCards metrics={data.metrics} />

          {/* Distribuciones Gráficas por Prioridad, Canal y Estado */}
          <DashboardDistributionsView distributions={data.distributions} />

          {/* Sección inferior: Leads de atención urgente y rendimiento por punto de venta */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <AttentionLeadsTable leads={data.attentionLeads} />
            <SalesPointsTable salesPoints={data.salesPoints} />
          </div>
        </div>
      )}
    </div>
  )
}
