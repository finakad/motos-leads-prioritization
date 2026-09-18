import { z } from 'zod'

export const MotorcycleApiSchema = z.object({
  sku: z.string(),
  brand: z.string(),
  line: z.string(),
  engine_displacement_cc: z.number(),
  segment: z.string(),
  list_price: z.number(),
  reported_available_units: z.number(),
  available_sales_points: z.array(z.string()).default([]),
})

export type MotorcycleApi = z.infer<typeof MotorcycleApiSchema>

export const MotorcycleListResponseApiSchema = z.object({
  items: z.array(MotorcycleApiSchema),
  total: z.number(),
  brands: z.array(z.string()).default([]),
  segments: z.array(z.string()).default([]),
})

export type MotorcycleListResponseApi = z.infer<typeof MotorcycleListResponseApiSchema>
