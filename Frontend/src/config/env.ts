import { z } from 'zod'

const envSchema = z.object({
  VITE_API_URL: z.string().default('http://127.0.0.1:8000/api/v1'),
  VITE_USE_MOCKS: z
    .string()
    .optional()
    .transform((val) => val === undefined || val === 'true' || val === '1'),
  VITE_COMPANY_ID: z.string().default('empresa-motos-001'),
  VITE_COMPANY_NAME: z.string().default('MotoCenter Principal'),
  VITE_STORE_NAME: z.string().default('Sede Central'),
})

const parsed = envSchema.safeParse(import.meta.env)

export const env = {
  apiUrl: parsed.success ? parsed.data.VITE_API_URL : 'http://127.0.0.1:8000/api/v1',
  useMocks: parsed.success ? parsed.data.VITE_USE_MOCKS : true,
  companyId: parsed.success ? parsed.data.VITE_COMPANY_ID : 'empresa-motos-001',
  companyName: parsed.success ? parsed.data.VITE_COMPANY_NAME : 'MotoCenter Principal',
  storeName: parsed.success ? parsed.data.VITE_STORE_NAME : 'Sede Central',
}
