export interface DashboardKpiMetrics {
  totalLeads: number
  highPriorityLeads: number
  mediumPriorityLeads: number
  lowPriorityLeads: number
  unscoredLeads: number
  averageScore: number | null
  sampleSize: number
  isTotalCensus: boolean
}

export interface DistributionItem {
  label: string
  value: number
  percentage: number
}

export interface DashboardDistributions {
  priority: DistributionItem[]
  channel: DistributionItem[]
  managementStatus: DistributionItem[]
  salesPoint: DistributionItem[]
}

export interface SalesPointKpiRow {
  companyId: string
  salesPointId: string
  totalLeads: number
  highPriorityLeads: number
  averageScore: number | null
}

export interface AttentionLeadItem {
  id: string
  customerName: string
  phoneMasked: string
  salesPointId: string
  channel: string
  modelInterest: string
  score: number | null
  priorityTier: 'ALTA' | 'MEDIA' | 'BAJA' | null
  conversionProbability: number | null
}

export interface DashboardMetadata {
  companyId: string
  dataSource: 'api' | 'mock'
  isDerived: boolean
  sampleSize: number
  totalCompanyLeads: number
  syncTime: string
  notice?: string
}

export interface DashboardData {
  metrics: DashboardKpiMetrics
  distributions: DashboardDistributions
  salesPoints: SalesPointKpiRow[]
  attentionLeads: AttentionLeadItem[]
  metadata: DashboardMetadata
}
