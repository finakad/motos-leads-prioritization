export type AdvisorStatus = 'active' | 'inactive'

export interface Advisor {
  id: string
  companyId: string
  salesPointId: string
  fullName: string
  dailyLeadCapacity: number
  status: AdvisorStatus
  joinedAt: string | null
}

export interface AdvisorWorkload {
  advisorId: string
  totalLeadsAtSalesPoint: number
  highPriorityLeadsAtSalesPoint: number
  estimatedLeadsPerAdvisor: number
  capacityUtilizationPercent: number | null
}

export interface EnrichedAdvisor extends Advisor {
  workload: AdvisorWorkload
}

export interface AdvisorsFilterParams {
  search?: string
  companyId?: string | 'all'
  salesPointId?: string | 'all'
  status?: AdvisorStatus | 'all'
}

export interface SalesPointSummary {
  companyId: string
  salesPointId: string
  activeAdvisorsCount: number
  dailyCapacityTotal: number
  totalLeads: number
  highPriorityLeads: number
  estimatedLeadsPerAdvisor: number
  capacityUtilizationPercent: number | null
}

export interface AdvisorsGeneralStats {
  totalAdvisors: number
  activeAdvisors: number
  inactiveAdvisors: number
  totalActiveDailyCapacity: number
  totalLeadsAtVisibleSalesPoints: number
  totalHighPriorityLeadsAtVisibleSalesPoints: number
}
