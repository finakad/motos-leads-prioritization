import type {
  Advisor,
  AdvisorWorkload,
  EnrichedAdvisor,
  AdvisorsFilterParams,
  SalesPointSummary,
  AdvisorsGeneralStats,
} from './advisor.types'
import type { PrioritizedLead } from '@/features/leads'

/**
 * Calcula la carga y métricas operativas agregadas por punto de venta,
 * reutilizando los leads mock existentes sin inventar asignaciones individuales.
 */
export function computeSalesPointWorkloadMap(
  advisors: Advisor[],
  leads: PrioritizedLead[]
): Map<
  string,
  {
    totalLeads: number
    highPriorityLeads: number
    activeAdvisorsCount: number
    dailyCapacityTotal: number
    estimatedLeadsPerAdvisor: number
    capacityUtilizationPercent: number | null
  }
> {
  const map = new Map<
    string,
    {
      totalLeads: number
      highPriorityLeads: number
      activeAdvisorsCount: number
      dailyCapacityTotal: number
      estimatedLeadsPerAdvisor: number
      capacityUtilizationPercent: number | null
    }
  >()

  // Extraer todos los puntos de venta presentes
  const salesPointIds = new Set<string>()
  advisors.forEach((a) => salesPointIds.add(a.salesPointId))
  leads.forEach((l) => salesPointIds.add(l.salesPointId))

  salesPointIds.forEach((spId) => {
    const leadsInSp = leads.filter((l) => l.salesPointId === spId)
    const totalLeads = leadsInSp.length
    const highPriorityLeads = leadsInSp.filter((l) => l.priority === 'high').length

    const activeAdvisorsInSp = advisors.filter(
      (a) => a.salesPointId === spId && a.status === 'active'
    )
    const activeAdvisorsCount = activeAdvisorsInSp.length
    const dailyCapacityTotal = activeAdvisorsInSp.reduce(
      (acc, a) => acc + a.dailyLeadCapacity,
      0
    )

    const estimatedLeadsPerAdvisor =
      activeAdvisorsCount > 0
        ? Number((totalLeads / activeAdvisorsCount).toFixed(1))
        : 0

    // Regla: total de leads / capacidad diaria total de asesores activos * 100.
    // Si no hay asesores activos o capacidad es cero -> null ("No disponible")
    const capacityUtilizationPercent =
      dailyCapacityTotal > 0
        ? Number(((totalLeads / dailyCapacityTotal) * 100).toFixed(1))
        : null

    map.set(spId, {
      totalLeads,
      highPriorityLeads,
      activeAdvisorsCount,
      dailyCapacityTotal,
      estimatedLeadsPerAdvisor,
      capacityUtilizationPercent,
    })
  })

  return map
}

/**
 * Enriquece cada asesor con su carga operativa calculada a nivel de punto de venta.
 */
export function enrichAdvisorsWithWorkload(
  advisors: Advisor[],
  leads: PrioritizedLead[]
): EnrichedAdvisor[] {
  const workloadMap = computeSalesPointWorkloadMap(advisors, leads)

  return advisors.map((advisor) => {
    const spStats = workloadMap.get(advisor.salesPointId) || {
      totalLeads: 0,
      highPriorityLeads: 0,
      activeAdvisorsCount: 0,
      dailyCapacityTotal: 0,
      estimatedLeadsPerAdvisor: 0,
      capacityUtilizationPercent: null,
    }

    const workload: AdvisorWorkload = {
      advisorId: advisor.id,
      totalLeadsAtSalesPoint: spStats.totalLeads,
      highPriorityLeadsAtSalesPoint: spStats.highPriorityLeads,
      estimatedLeadsPerAdvisor: spStats.estimatedLeadsPerAdvisor,
      capacityUtilizationPercent: spStats.capacityUtilizationPercent,
    }

    return {
      ...advisor,
      workload,
    }
  })
}

/**
 * Filtra y ordena inicialmente los asesores por empresa, punto de venta y nombre.
 */
export function filterAndSortAdvisors(
  advisors: EnrichedAdvisor[],
  filters: AdvisorsFilterParams
): EnrichedAdvisor[] {
  const filtered = advisors.filter((advisor) => {
    // Búsqueda por nombre o ID
    if (filters.search && filters.search.trim().length > 0) {
      const q = filters.search.toLowerCase().trim()
      const matchName = advisor.fullName.toLowerCase().includes(q)
      const matchId = advisor.id.toLowerCase().includes(q)
      if (!matchName && !matchId) return false
    }

    // Filtro por empresa
    if (filters.companyId && filters.companyId !== 'all') {
      if (advisor.companyId !== filters.companyId) return false
    }

    // Filtro por punto de venta
    if (filters.salesPointId && filters.salesPointId !== 'all') {
      if (advisor.salesPointId !== filters.salesPointId) return false
    }

    // Filtro por estado
    if (filters.status && filters.status !== 'all') {
      if (advisor.status !== filters.status) return false
    }

    return true
  })

  // Orden inicial: empresa, punto de venta y nombre
  filtered.sort((a, b) => {
    const cmpCompany = a.companyId.localeCompare(b.companyId)
    if (cmpCompany !== 0) return cmpCompany

    const cmpSp = a.salesPointId.localeCompare(b.salesPointId)
    if (cmpSp !== 0) return cmpSp

    return a.fullName.localeCompare(b.fullName)
  })

  return filtered
}

/**
 * Genera el resumen compacto por punto de venta ordenado por:
 * mayor número de leads de prioridad alta y luego por total de leads.
 */
export function computeSalesPointSummaries(
  advisors: Advisor[],
  leads: PrioritizedLead[],
  filters: AdvisorsFilterParams
): SalesPointSummary[] {
  const workloadMap = computeSalesPointWorkloadMap(advisors, leads)

  // Encontrar pares únicos (companyId, salesPointId)
  const spCompanyMap = new Map<string, string>()
  advisors.forEach((a) => spCompanyMap.set(a.salesPointId, a.companyId))
  leads.forEach((l) => {
    if (!spCompanyMap.has(l.salesPointId)) {
      spCompanyMap.set(l.salesPointId, l.companyId)
    }
  })

  const summaries: SalesPointSummary[] = []

  spCompanyMap.forEach((companyId, salesPointId) => {
    // Aplicar filtros de empresa y punto de venta si corresponden
    if (filters.companyId && filters.companyId !== 'all' && companyId !== filters.companyId) {
      return
    }
    if (filters.salesPointId && filters.salesPointId !== 'all' && salesPointId !== filters.salesPointId) {
      return
    }

    const stats = workloadMap.get(salesPointId) || {
      totalLeads: 0,
      highPriorityLeads: 0,
      activeAdvisorsCount: 0,
      dailyCapacityTotal: 0,
      estimatedLeadsPerAdvisor: 0,
      capacityUtilizationPercent: null,
    }

    summaries.push({
      companyId,
      salesPointId,
      activeAdvisorsCount: stats.activeAdvisorsCount,
      dailyCapacityTotal: stats.dailyCapacityTotal,
      totalLeads: stats.totalLeads,
      highPriorityLeads: stats.highPriorityLeads,
      estimatedLeadsPerAdvisor: stats.estimatedLeadsPerAdvisor,
      capacityUtilizationPercent: stats.capacityUtilizationPercent,
    })
  })

  // Ordenar por mayor número de leads de prioridad alta y luego por total de leads
  summaries.sort((a, b) => {
    const diffHigh = b.highPriorityLeads - a.highPriorityLeads
    if (diffHigh !== 0) return diffHigh
    return b.totalLeads - a.totalLeads
  })

  return summaries
}

/**
 * Calcula los 6 indicadores generales para los asesores visibles:
 * - total de asesores visibles;
 * - asesores activos;
 * - asesores inactivos;
 * - capacidad diaria total de los asesores activos visibles;
 * - total de leads en los puntos de venta visibles;
 * - total de leads de prioridad alta en los puntos de venta visibles.
 */
export function computeAdvisorsGeneralStats(
  visibleAdvisors: EnrichedAdvisor[],
  leads: PrioritizedLead[]
): AdvisorsGeneralStats {
  const activeAdvisorsList = visibleAdvisors.filter((a) => a.status === 'active')
  const inactiveAdvisorsList = visibleAdvisors.filter((a) => a.status === 'inactive')

  const totalActiveDailyCapacity = activeAdvisorsList.reduce(
    (acc, a) => acc + a.dailyLeadCapacity,
    0
  )

  // Obtener los puntos de venta visibles únicos
  const visibleSpIds = new Set<string>()
  visibleAdvisors.forEach((a) => visibleSpIds.add(a.salesPointId))

  const leadsAtVisibleSp = leads.filter((l) => visibleSpIds.has(l.salesPointId))
  const totalLeadsAtVisibleSalesPoints = leadsAtVisibleSp.length
  const totalHighPriorityLeadsAtVisibleSalesPoints = leadsAtVisibleSp.filter(
    (l) => l.priority === 'high'
  ).length

  return {
    totalAdvisors: visibleAdvisors.length,
    activeAdvisors: activeAdvisorsList.length,
    inactiveAdvisors: inactiveAdvisorsList.length,
    totalActiveDailyCapacity,
    totalLeadsAtVisibleSalesPoints,
    totalHighPriorityLeadsAtVisibleSalesPoints,
  }
}

/**
 * Devuelve las listas únicas de empresas y puntos de venta para los selectores de filtro.
 */
export function getFilterOptions(
  advisors: Advisor[],
  selectedCompanyId?: string | 'all'
): { companies: string[]; salesPoints: string[] } {
  const compSet = new Set<string>()
  const spSet = new Set<string>()

  advisors.forEach((a) => {
    compSet.add(a.companyId)
    // Si hay empresa seleccionada y no es 'all', filtrar puntos de venta
    if (!selectedCompanyId || selectedCompanyId === 'all' || a.companyId === selectedCompanyId) {
      spSet.add(a.salesPointId)
    }
  })

  return {
    companies: Array.from(compSet).sort(),
    salesPoints: Array.from(spSet).sort(),
  }
}
