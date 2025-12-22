import type { IncomingMessage } from 'http';

/**
 * SSR render handler (stub for SPA mode).
 * @param {IncomingMessage} _req - The incoming HTTP request (unused in SPA mode)
 * @returns {Promise<string>} An HTML string (returns empty for SPA)
 */
export async function render(_req: IncomingMessage): Promise<string> {
  return '';
}
