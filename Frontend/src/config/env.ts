export type DataSource = 'api' | 'mock'

export interface AppEnv {
  apiBaseUrl: string
  dataSource: DataSource
  defaultCompanyId: string
}

// Acceso seguro a variables de entorno tanto en Vite como en entornos Node / pruebas
const metaEnv =
  typeof import.meta !== 'undefined' && import.meta.env
    ? import.meta.env
    : (typeof process !== 'undefined' && process.env ? process.env : {})

const rawDataSource = (metaEnv.VITE_DATA_SOURCE as string | undefined)?.toLowerCase()
const dataSource: DataSource = rawDataSource === 'mock' ? 'mock' : 'api'

export const env: AppEnv = {
  apiBaseUrl:
    (metaEnv.VITE_API_BASE_URL as string | undefined) ||
    (metaEnv.FRONTEND_API_BASE_URL as string | undefined) ||
    'http://127.0.0.1:8000',
  dataSource,
  defaultCompanyId:
    (metaEnv.VITE_DEFAULT_COMPANY_ID as string | undefined) || 'EMP-01',
} as const
