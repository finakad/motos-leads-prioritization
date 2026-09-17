export type LeadPriority = 'high' | 'medium' | 'low'

export interface PrioritizedLead {
  id: string
  companyId: string
  salesPointId: string
  customerName: string
  channel: string | null
  managementStatus: string | null
  modelInterestText: string | null
  registeredAt: string | null
  priority: LeadPriority
  score: number | null
}

export interface ScoreFactor {
  label: string
  description: string
  impact: 'positive' | 'neutral' | 'negative'
}

export interface ConversationMessage {
  id: string
  sender: string
  sentAt: string
  text: string
}

export interface LeadConversation {
  id: string
  channel: string
  startedAt: string
  messages: ConversationMessage[]
}

export interface LeadDetail extends PrioritizedLead {
  firstContactAt: string | null
  campaign: string | null
  city: string | null
  scoreExplanation: string | null
  scoreFactors: ScoreFactor[]
  conversations: LeadConversation[]
}

export interface LeadsFilterParams {
  search?: string
  priority?: LeadPriority | 'all'
  channel?: string | 'all'
  managementStatus?: string | 'all'
  salesPointId?: string | 'all'
}

export interface LeadsSummaryStats {
  total: number
  high: number
  medium: number
  low: number
}
