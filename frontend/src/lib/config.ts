export const isServer = typeof window === 'undefined';

/**
 * Normalize URL by removing trailing slash.
 * @param {string} value - The URL to normalize
 * @returns {string} The normalized URL
 */
const normalizeUrl = (value: string | undefined): string =>
  value?.endsWith('/') ? value.slice(0, -1) : value ?? '';

export const appConfig = {
  apiUrl: normalizeUrl(import.meta.env.VITE_API_URL) ?? 'http://localhost:5000',
  wsUrl: normalizeUrl(import.meta.env.VITE_WS_URL) ?? '',
  logLevel: (import.meta.env.VITE_LOG_LEVEL ?? import.meta.env.LOG_LEVEL ?? 'info').toLowerCase(),
  logTarget: (import.meta.env.VITE_LOG_TARGET ?? import.meta.env.LOG_TARGET ?? 'console').toLowerCase(),
  pollIntervalMs: Number(import.meta.env.VITE_POLL_INTERVAL_MS ?? 1500),
};

export type AppConfig = typeof appConfig
