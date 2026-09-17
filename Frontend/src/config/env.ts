export const env = {
  apiBaseUrl:
    (import.meta.env.FRONTEND_API_BASE_URL as string | undefined) ||
    (import.meta.env.VITE_API_BASE_URL as string | undefined) ||
    '',
} as const
