import type { AdvisorResponseApi } from './advisors.schemas'
import type { Advisor } from './advisor.types'

/**
 * Adapta la respuesta del backend FastAPI (snake_case) al modelo Advisor del frontend.
 */
export function adaptApiAdvisor(item: AdvisorResponseApi): Advisor {
  return {
    id: item.id,
    companyId: item.company_id,
    salesPointId: item.sales_point_id,
    fullName: item.full_name,
    dailyLeadCapacity: item.daily_lead_capacity,
    status: item.is_active ? 'active' : 'inactive',
    joinedAt: item.hired_at,
  }
}
