import { z } from 'zod'

export const LeadPrioritySchema = z.enum(['ALTA', 'MEDIA', 'BAJA'])
export type LeadPriority = z.infer<typeof LeadPrioritySchema>

export const LeadStatusSchema = z.enum([
  'NUEVO',
  'CONTACTADO',
  'EN_GESTION',
  'CALIFICADO',
  'DESCARTADO',
  'VENTA_CERRADA',
])
export type LeadStatus = z.infer<typeof LeadStatusSchema>

export const LeadChannelSchema = z.enum([
  'WHATSAPP',
  'WEB',
  'INSTAGRAM',
  'FACEBOOK',
  'CONCESIONARIO',
])
export type LeadChannel = z.infer<typeof LeadChannelSchema>

export const ScoreFactorSchema = z.object({
  id: z.string(),
  factor: z.string(),
  impact: z.enum(['POSITIVO', 'NEUTRAL', 'NEGATIVO']),
  points: z.number(),
  explanation: z.string(),
})
export type ScoreFactor = z.infer<typeof ScoreFactorSchema>

export const CommercialSignalSchema = z.object({
  id: z.string(),
  type: z.string(),
  description: z.string(),
  detectedAt: z.string(),
})
export type CommercialSignal = z.infer<typeof CommercialSignalSchema>

export const ConversationMessageSchema = z.object({
  id: z.string(),
  sender: z.enum(['LEAD', 'BOT', 'ASESOR']),
  message: z.string(),
  timestamp: z.string(),
})
export type ConversationMessage = z.infer<typeof ConversationMessageSchema>

export const LeadSchema = z.object({
  id: z.string(),
  companyId: z.string(),
  storeName: z.string(),
  fullName: z.string(),
  phone: z.string(),
  email: z.string().email().optional(),
  channel: LeadChannelSchema,
  status: LeadStatusSchema,
  modelOfInterest: z.string(),
  modelPrice: z.number().optional(),
  registrationDate: z.string(),
  lastInteractionDate: z.string(),
  score: z.number().min(0).max(100),
  priority: LeadPrioritySchema,
  scoreExplanation: z.object({
    summary: z.string(),
    confidence: z.number().min(0).max(1),
    keyDrivers: z.array(ScoreFactorSchema),
  }),
  commercialSignals: z.array(CommercialSignalSchema),
  recentMessages: z.array(ConversationMessageSchema).optional(),
  assignedAdvisor: z
    .object({
      id: z.string(),
      name: z.string(),
      email: z.string().optional(),
    })
    .nullable()
    .optional(),
})

export type Lead = z.infer<typeof LeadSchema>

export const LeadsFilterSchema = z.object({
  search: z.string().optional(),
  priority: z.union([LeadPrioritySchema, z.literal('TODAS')]).optional(),
  status: z.union([LeadStatusSchema, z.literal('TODOS')]).optional(),
  channel: z.union([LeadChannelSchema, z.literal('TODOS')]).optional(),
})

export type LeadsFilter = z.infer<typeof LeadsFilterSchema>

export interface LeadsListResponse {
  data: Lead[]
  total: number
  companyId: string
}
