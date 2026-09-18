import type { LeadPrioritizedItemApi } from './dashboard.schemas'
import type {
  DashboardData,
  DashboardDistributions,
  DashboardKpiMetrics,
  DistributionItem,
  SalesPointKpiRow,
  AttentionLeadItem,
  DashboardMetadata,
} from './dashboard.types'

/**
 * Calcula las métricas KPI principales a partir del arreglo de leads priorizados.
 */
export function computeDashboardMetrics(
  leads: LeadPrioritizedItemApi[],
  totalCompanyLeads: number
): DashboardKpiMetrics {
  const sampleSize = leads.length
  let highCount = 0
  let mediumCount = 0
  let lowCount = 0
  let unscoredCount = 0
  let scoreSum = 0
  let scoreCount = 0

  for (const lead of leads) {
    if (lead.priority_tier === 'ALTA') {
      highCount++
    } else if (lead.priority_tier === 'MEDIA') {
      mediumCount++
    } else if (lead.priority_tier === 'BAJA') {
      lowCount++
    } else {
      unscoredCount++
    }

    if (lead.score !== null && lead.score !== undefined && !Number.isNaN(lead.score)) {
      scoreSum += lead.score
      scoreCount++
    }
  }

  const averageScore =
    scoreCount > 0 ? Math.round((scoreSum / scoreCount) * 10) / 10 : null

  return {
    totalLeads: totalCompanyLeads > 0 ? totalCompanyLeads : sampleSize,
    highPriorityLeads: highCount,
    mediumPriorityLeads: mediumCount,
    lowPriorityLeads: lowCount,
    unscoredLeads: unscoredCount,
    averageScore,
    sampleSize,
    isTotalCensus: sampleSize >= totalCompanyLeads && totalCompanyLeads > 0,
  }
}

function buildDistribution(
  counts: Record<string, number>,
  total: number
): DistributionItem[] {
  if (total === 0) return []

  return Object.entries(counts)
    .map(([label, value]) => ({
      label,
      value,
      percentage: Math.round((value / total) * 1000) / 10,
    }))
    .sort((a, b) => b.value - a.value)
}

/**
 * Agrupa y genera distribuciones por prioridad, canal, estado de gestión y punto de venta.
 */
export function computeDashboardDistributions(
  leads: LeadPrioritizedItemApi[]
): DashboardDistributions {
  const total = leads.length

  const priorityCounts: Record<string, number> = {
    ALTA: 0,
    MEDIA: 0,
    BAJA: 0,
    'SIN PRIORIDAD': 0,
  }
  const channelCounts: Record<string, number> = {}
  const statusCounts: Record<string, number> = {}
  const spCounts: Record<string, number> = {}

  for (const lead of leads) {
    if (lead.priority_tier === 'ALTA') priorityCounts.ALTA++
    else if (lead.priority_tier === 'MEDIA') priorityCounts.MEDIA++
    else if (lead.priority_tier === 'BAJA') priorityCounts.BAJA++
    else priorityCounts['SIN PRIORIDAD']++

    const ch = (lead.channel || 'DESCONOCIDO').toUpperCase()
    channelCounts[ch] = (channelCounts[ch] || 0) + 1

    const st = (lead.management_status || 'SIN ESTADO').toUpperCase()
    statusCounts[st] = (statusCounts[st] || 0) + 1

    const sp = lead.sales_point_id || 'SIN ASIGNAR'
    spCounts[sp] = (spCounts[sp] || 0) + 1
  }

  const priorityItems =
    total === 0
      ? []
      : Object.entries(priorityCounts)
          .filter(([, count]) => count > 0 || total > 0)
          .map(([label, value]) => ({
            label,
            value,
            percentage: total > 0 ? Math.round((value / total) * 1000) / 10 : 0,
          }))

  return {
    priority: priorityItems,
    channel: buildDistribution(channelCounts, total),
    managementStatus: buildDistribution(statusCounts, total),
    salesPoint: buildDistribution(spCounts, total),
  }
}

/**
 * Agrupa y genera las métricas por sede / punto de venta.
 */
export function computeSalesPointKpis(
  leads: LeadPrioritizedItemApi[],
  companyId: string
): SalesPointKpiRow[] {
  const groups: Record<
    string,
    { total: number; high: number; scoreSum: number; scoreCount: number }
  > = {}

  for (const lead of leads) {
    const spId = lead.sales_point_id || 'SIN_ASIGNAR'
    if (!groups[spId]) {
      groups[spId] = { total: 0, high: 0, scoreSum: 0, scoreCount: 0 }
    }
    groups[spId].total++
    if (lead.priority_tier === 'ALTA') {
      groups[spId].high++
    }
    if (lead.score !== null && lead.score !== undefined && !Number.isNaN(lead.score)) {
      groups[spId].scoreSum += lead.score
      groups[spId].scoreCount++
    }
  }

  return Object.entries(groups)
    .map(([salesPointId, data]) => ({
      companyId,
      salesPointId,
      totalLeads: data.total,
      highPriorityLeads: data.high,
      averageScore:
        data.scoreCount > 0
          ? Math.round((data.scoreSum / data.scoreCount) * 10) / 10
          : null,
    }))
    .sort((a, b) => b.highPriorityLeads - a.highPriorityLeads || b.totalLeads - a.totalLeads)
}

/**
 * Extrae los 5 leads de mayor prioridad comercial.
 */
export function computeAttentionLeads(
  leads: LeadPrioritizedItemApi[]
): AttentionLeadItem[] {
  const sorted = [...leads].sort((a, b) => {
    const scoreA = a.score ?? -1
    const scoreB = b.score ?? -1
    return scoreB - scoreA
  })

  return sorted.slice(0, 5).map((l) => ({
    id: l.lead_id,
    customerName: l.customer_name || 'Prospecto sin nombre',
    phoneMasked: l.phone_masked || '***-***-****',
    salesPointId: l.sales_point_id || 'N/D',
    channel: l.channel || 'Desconocido',
    modelInterest: l.model_interest || 'Sin especificar',
    score: l.score ?? null,
    priorityTier: l.priority_tier ?? null,
    conversionProbability: l.conversion_probability ?? null,
  }))
}

/**
 * Convierte los datos crudos validados en el contrato unificado de DashboardData.
 */
export function adaptApiLeadsToDashboard(
  items: LeadPrioritizedItemApi[],
  totalCompanyLeads: number,
  companyId: string,
  dataSource: 'api' | 'mock'
): DashboardData {
  const metrics = computeDashboardMetrics(items, totalCompanyLeads)
  const distributions = computeDashboardDistributions(items)
  const salesPoints = computeSalesPointKpis(items, companyId)
  const attentionLeads = computeAttentionLeads(items)

  const isFullCensus = items.length >= totalCompanyLeads && totalCompanyLeads > 0
  const notice =
    dataSource === 'api'
      ? `Métricas comerciales calculadas por derivación local a partir de ${items.length} leads priorizados (${
          isFullCensus ? 'censo total 100%' : `muestra de ${items.length} de ${totalCompanyLeads}`
        }) obtenidos desde GET /api/v1/companies/${companyId}/leads/prioritized. (FastAPI no expone endpoint agregador /metrics).`
      : `Datos simulados en modo local/mock para la empresa ${companyId}.`

  const metadata: DashboardMetadata = {
    companyId,
    dataSource,
    isDerived: dataSource === 'api',
    sampleSize: items.length,
    totalCompanyLeads,
    syncTime: new Date().toLocaleTimeString('es-CO', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    }),
    notice,
  }

  return {
    metrics,
    distributions,
    salesPoints,
    attentionLeads,
    metadata,
  }
}
