export class HttpError extends Error {
  public status: number
  public details?: unknown

  constructor(message: string, status: number, details?: unknown) {
    super(message)
    this.name = 'HttpError'
    this.status = status
    this.details = details
  }
}

export function isHttpError(error: unknown): error is HttpError {
  return error instanceof HttpError
}
