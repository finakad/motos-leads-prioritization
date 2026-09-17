import { env } from '@/config/env'
import { HttpError } from './errors'

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined>
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { params, headers, ...customConfig } = options

  let url = `${env.apiUrl}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`
  if (params) {
    const searchParams = new URLSearchParams()
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined) {
        searchParams.append(key, String(value))
      }
    }
    const queryString = searchParams.toString()
    if (queryString) {
      url += `?${queryString}`
    }
  }

  const defaultHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    'X-Company-ID': env.companyId,
  }

  const response = await fetch(url, {
    ...customConfig,
    headers: {
      ...defaultHeaders,
      ...headers,
    },
  })

  if (!response.ok) {
    let errorDetails: unknown
    try {
      errorDetails = await response.json()
    } catch {
      errorDetails = await response.text()
    }
    throw new HttpError(
      `Error en solicitud HTTP: ${response.status} ${response.statusText}`,
      response.status,
      errorDetails
    )
  }

  if (response.status === 204) {
    return {} as T
  }

  return (await response.json()) as T
}
