import { z } from 'zod'
import { apiClient } from './apiClient'

export const HealthStatusSchema = z.object({
  status: z.string(),
  environment: z.string().optional(),
})

export type HealthStatus = z.infer<typeof HealthStatusSchema>

export const DatabaseHealthSchema = z.object({
  database: z.string(),
})

export type DatabaseHealth = z.infer<typeof DatabaseHealthSchema>

export const healthService = {
  async checkHealth(): Promise<HealthStatus> {
    const raw = await apiClient.get<unknown>('/health')
    return HealthStatusSchema.parse(raw)
  },

  async checkDatabase(): Promise<DatabaseHealth> {
    const raw = await apiClient.get<unknown>('/health/database')
    return DatabaseHealthSchema.parse(raw)
  },
}
