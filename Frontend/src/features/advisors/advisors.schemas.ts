import { z } from 'zod'

export const AdvisorResponseApiSchema = z.object({
  id: z.string(),
  full_name: z.string(),
  sales_point_id: z.string(),
  company_id: z.string(),
  daily_lead_capacity: z.number(),
  is_active: z.boolean(),
  hired_at: z.string(),
})

export type AdvisorResponseApi = z.infer<typeof AdvisorResponseApiSchema>

export const AdvisorsListResponseApiSchema = z.array(AdvisorResponseApiSchema)
export type AdvisorsListResponseApi = z.infer<typeof AdvisorsListResponseApiSchema>
