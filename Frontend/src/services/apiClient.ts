import { env } from '@/config/env'
import {
  ApiError,
  ApiNetworkError,
  ApiNotFoundError,
  ApiValidationError,
  type ValidationErrorField,
} from './apiErrors'

export { ApiError, ApiNetworkError, ApiNotFoundError, ApiValidationError }

export interface RequestOptions extends Omit<RequestInit, 'signal'> {
  params?: Record<string, string | number | boolean | null | undefined>
  companyId?: string
  timeoutMs?: number
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { params, headers, companyId, timeoutMs = 15000, ...customConfig } = options

  const baseUrl = env.apiBaseUrl.replace(/\/$/, '')
  const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
  let url = baseUrl ? `${baseUrl}${normalizedEndpoint}` : normalizedEndpoint

  if (params) {
    const searchParams = new URLSearchParams()
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null) {
        searchParams.append(key, String(value))
      }
    }
    const queryString = searchParams.toString()
    if (queryString) {
      url += `?${queryString}`
    }
  }

  const effectiveHeaders: Record<string, string> = {
    Accept: 'application/json',
    'Content-Type': 'application/json',
    ...(companyId ? { 'X-Company-ID': companyId } : {}),
    ...(headers as Record<string, string> | undefined),
  }

  let response: Response
  try {
    const signal = AbortSignal.timeout(timeoutMs)
    response = await fetch(url, {
      ...customConfig,
      headers: effectiveHeaders,
      signal,
    })
  } catch (error: unknown) {
    if (error instanceof Error && error.name === 'TimeoutError') {
      throw new ApiNetworkError(
        `La solicitud al servidor backend superó el tiempo de espera (${timeoutMs / 1000}s).`,
        error
      )
    }
    // Error de red (CORS, servidor no disponible, socket cerrado)
    throw new ApiNetworkError(
      'No fue posible conectar con el servidor backend. Verifique que FastAPI esté activo en http://127.0.0.1:8000.',
      error
    )
  }

  if (!response.ok) {
    let errorData: unknown
    try {
      errorData = await response.json()
    } catch {
      try {
        errorData = await response.text()
      } catch {
        errorData = null
      }
    }

    if (response.status === 404) {
      const detailMsg =
        typeof errorData === 'object' && errorData !== null && 'detail' in errorData
          ? String((errorData as { detail: unknown }).detail)
          : 'El recurso solicitado no fue encontrado en el backend.'
      throw new ApiNotFoundError(detailMsg, errorData)
    }

    if (response.status === 422) {
      let validationItems: ValidationErrorField[] = []
      if (
        typeof errorData === 'object' &&
        errorData !== null &&
        'detail' in errorData &&
        Array.isArray((errorData as { detail: unknown }).detail)
      ) {
        validationItems = (errorData as { detail: ValidationErrorField[] }).detail
      }
      throw new ApiValidationError(
        'Los datos enviados no superaron la validación del backend (HTTP 422).',
        validationItems,
        errorData
      )
    }

    if (response.status >= 500) {
      throw new ApiError(
        `Error interno del servidor backend (HTTP ${response.status}). Intente nuevamente más tarde.`,
        response.status,
        response.statusText,
        errorData
      )
    }

    const genericMsg =
      typeof errorData === 'object' && errorData !== null && 'detail' in errorData
        ? String((errorData as { detail: unknown }).detail)
        : `Error en solicitud API: ${response.status} ${response.statusText}`

    throw new ApiError(genericMsg, response.status, response.statusText, errorData)
  }

  if (response.status === 204) {
    return {} as T
  }

  try {
    return (await response.json()) as T
  } catch (parseError) {
    throw new ApiError(
      'La respuesta del servidor no tiene un formato JSON válido.',
      response.status,
      response.statusText,
      parseError
    )
  }
}

export const apiClient = {
  get: <T>(endpoint: string, options?: RequestOptions) =>
    request<T>(endpoint, { ...options, method: 'GET' }),

  post: <T>(endpoint: string, body?: unknown, options?: RequestOptions) =>
    request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }),

  put: <T>(endpoint: string, body?: unknown, options?: RequestOptions) =>
    request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }),

  patch: <T>(endpoint: string, body?: unknown, options?: RequestOptions) =>
    request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }),

  delete: <T>(endpoint: string, options?: RequestOptions) =>
    request<T>(endpoint, { ...options, method: 'DELETE' }),
}
