export class ApiError extends Error {
  public status: number
  public statusText?: string
  public details?: unknown

  constructor(message: string, status: number, statusText?: string, details?: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.statusText = statusText
    this.details = details
  }
}

export class ApiNetworkError extends Error {
  public originalError?: unknown

  constructor(message = 'No fue posible conectar con el servidor backend. Verifique que FastAPI esté activo en http://127.0.0.1:8000.', originalError?: unknown) {
    super(message)
    this.name = 'ApiNetworkError'
    this.originalError = originalError
  }
}

export class ApiNotFoundError extends ApiError {
  constructor(message = 'El recurso solicitado no fue encontrado.', details?: unknown) {
    super(message, 404, 'Not Found', details)
    this.name = 'ApiNotFoundError'
  }
}

export interface ValidationErrorField {
  loc: (string | number)[]
  msg: string
  type: string
}

export class ApiValidationError extends ApiError {
  public validationErrors: ValidationErrorField[]

  constructor(message: string, validationErrors: ValidationErrorField[] = [], details?: unknown) {
    super(message, 422, 'Unprocessable Entity', details)
    this.name = 'ApiValidationError'
    this.validationErrors = validationErrors
  }
}
