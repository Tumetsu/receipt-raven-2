/**
 * Prefix every API URL is built on: empty (same origin) unless `VITE_API_URL`
 * names a cross-origin backend. In production the backend serves the frontend,
 * and in development Vite proxies `/api`, so same origin is the default.
 */
export const API_BASE_URL: string = import.meta.env.VITE_API_URL ?? '';
