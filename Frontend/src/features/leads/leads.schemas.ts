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

export const LeadDetailResponseApiSchema = z.object({
  lead_id: z.string(),
  company_id: z.string(),
  sales_point_id: z.string(),
  customer_name: z.string().nullable().optional(),
  phone_masked: z.string().nullable().optional(),
  channel: z.string().nullable().optional(),
  city: z.string().nullable().optional(),
  model_interest_text: z.string().nullable().optional(),
  management_status: z.string().nullable().optional(),
  registered_at: z.string().nullable().optional(),
  first_contact_at: z.string().nullable().optional(),
  campaign: z.string().nullable().optional(),
  score: z.number().nullable().optional(),
  priority_tier: z.string().nullable().optional(),
  conversion_probability: z.number().nullable().optional(),
  has_conversation: z.boolean().default(false),
})
export type LeadDetailResponseApi = z.infer<typeof LeadDetailResponseApiSchema>

export const MessageDetailApiSchema = z.object({
  sequence_number: z.number(),
  sender: z.string(),
  message_time: z.string().nullable().optional(),
  text: z.string(),
})
export type MessageDetailApi = z.infer<typeof MessageDetailApiSchema>

export const ConversationDetailApiSchema = z.object({
  conversation_id: z.string(),
  channel: z.string().nullable().optional(),
  started_at: z.string().nullable().optional(),
  message_count: z.number(),
  messages: z.array(MessageDetailApiSchema),
})
export type ConversationDetailApi = z.infer<typeof ConversationDetailApiSchema>

export const LeadConversationsResponseApiSchema = z.object({
  lead_id: z.string(),
  company_id: z.string(),
  total_conversations: z.number(),
  conversations: z.array(ConversationDetailApiSchema),
})
export type LeadConversationsResponseApi = z.infer<typeof LeadConversationsResponseApiSchema>

export const FactorDetailApiSchema = z.object({
  name: z.string(),
  weight_pct: z.number(),
  score_obtained: z.number(),
  max_score: z.number(),
  description: z.string(),
  evidence: z.array(z.string()).optional().default([]),
})
export type FactorDetailApi = z.infer<typeof FactorDetailApiSchema>

export const LeadScoreDetailApiSchema = z.object({
  id: z.string().uuid().nullable().optional(),
  lead_id: z.string(),
  company_id: z.string(),
  sales_point_id: z.string(),
  customer_name: z.string().nullable().optional(),
  phone_normalized: z.string().nullable().optional(),
  channel: z.string().nullable().optional(),
  model_interest_text: z.string().nullable().optional(),
  score: z.number(),
  priority_tier: PriorityTierEnum,
  conversion_probability: z.number().nullable().optional(),
  factors: z.record(z.string(), FactorDetailApiSchema),
  evidence: z.array(z.record(z.string(), z.unknown())).optional().default([]),
  model_version: z.string(),
  calculated_at: z.string(),
})
export type LeadScoreDetailApi = z.infer<typeof LeadScoreDetailApiSchema>
