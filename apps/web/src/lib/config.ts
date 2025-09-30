export const API_BASE_URL =
  import.meta.env.VITE_API_URL ??
  import.meta.env.VITE_API_BASE_URL ??
  'http://localhost:8000'

export const CSRF_COOKIE_NAME = 'csrftoken'
export const CSRF_HEADER_NAME = 'x-csrftoken'

export const APP_NAME = import.meta.env.VITE_APP_NAME ?? 'SaaS Template'
