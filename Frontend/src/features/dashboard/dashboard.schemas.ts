import { z } from 'zod'

export const PriorityTierEnum = z.enum(['ALTA', 'MEDIA', 'BAJA'])
export type PriorityTierApi = z.infer<typeof PriorityTierEnum>

export const LeadPrioritizedItemApiSchema = z.object({
  lead_id: z.string(),
  company_id: z.string(),
  sales_point_id: z.string(),
  customer_name: z.string().nullable().optional(),
  phone_masked: z.string().nullable().optional(),
  channel: z.string().nullable().optional(),
  model_interest: z.string().nullable().optional(),
  management_status: z.string().nullable().optional(),
  registered_at: z.string().nullable().optional(),
  score: z.number().nullable().optional(),
  priority_tier: PriorityTierEnum.nullable().optional(),
  conversion_probability: z.number().nullable().optional(),
  has_conversation: z.boolean().default(false),
})
export type LeadPrioritizedItemApi = z.infer<typeof LeadPrioritizedItemApiSchema>

export const PaginatedLeadsResponseApiSchema = z.object({
  total: z.number(),
  page: z.number(),
  page_size: z.number(),
  total_pages: z.number(),
  items: z.array(LeadPrioritizedItemApiSchema),
})
export type PaginatedLeadsResponseApi = z.infer<typeof PaginatedLeadsResponseApiSchema>
