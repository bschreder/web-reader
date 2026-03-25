import pino from 'pino';
import type { Logger } from 'pino';
import path from 'path';
import fs from 'fs';

/**
 * Get log level from environment variable (default: info)
 * @returns {string} Log level string
 */
function getLogLevel(): string {
  const level = process.env.LOG_LEVEL || process.env.VITE_LOG_LEVEL || 'info';
  return level.toLowerCase();
}

/**
 * Get log target from environment variable (default: console)
 * Options: console, file, both
 * @returns {'console' | 'file' | 'both'} Log target
 */
function getLogTarget(): 'console' | 'file' | 'both' {
  const target = process.env.LOG_TARGET || process.env.VITE_LOG_TARGET || 'console';
  const normalized = target.toLowerCase() as 'console' | 'file' | 'both';
  return normalized === 'file' || normalized === 'both' ? normalized : 'console';
}

/**
 * Ensure logs directory exists
 * @returns {string} Path to logs directory
 */
function ensureLogsDirectory(): string {
  const logsDir = path.join(process.cwd(), 'logs');
  if (!fs.existsSync(logsDir)) {
    fs.mkdirSync(logsDir, { recursive: true });
  }
  return logsDir;
}

/**
 * Get today's log filename (YYYYMMDD format)
 * @returns {string} Log filename
 */
function getLogFilename(): string {
  const date = new Date();
  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, '0');
  const dd = String(date.getDate()).padStart(2, '0');
  return `log-frontend-${yyyy}${mm}${dd}.json`;
}

/**
 * Configure and create a Pino logger instance
 * @returns {Logger} Configured Pino logger
 */
function createLogger(): Logger {
  const level = getLogLevel();
  const target = getLogTarget();
  const logsDir = ensureLogsDirectory();
  const logFilename = getLogFilename();
  const logFilePath = path.join(logsDir, logFilename);

  // Determine transport based on target
  const transport =
    target === 'console'
      ? {
          target: 'pino-pretty',
          options: {
            colorize: true,
            translateTime: 'SYS:standard',
            ignore: 'pid,hostname',
            singleLine: false,
          },
        }
      : target === 'file'
        ? {
            target: 'pino/file',
            options: {
              destination: logFilePath,
            },
          }
        : [
            {
              target: 'pino-pretty',
              options: {
                colorize: true,
                translateTime: 'SYS:standard',
                ignore: 'pid,hostname',
                singleLine: false,
              },
            },
            {
              target: 'pino/file',
              options: {
                destination: logFilePath,
              },
            },
          ];

  const logger = pino(
    {
      level,
      timestamp: pino.stdTimeFunctions.isoTime,
    },
    target === 'console'
      ? pino.transport(transport)
      : target === 'file'
        ? pino.transport(transport)
        : pino.multistream(
            (transport as Array<{ target: string; options?: Record<string, unknown> }>).map((t) =>
              pino.transport(t)
            )
          )
  );

  return logger;
}

/**
 * Singleton logger instance
 */
let loggerInstance: Logger | null = null;

/**
 * Get or create the logger instance (only in Node.js environment)
 * @returns {Logger} The singleton logger instance
 */
export function getLogger(): Logger {
  // Only initialize in Node.js environment (SSR), not in browser
  if (!loggerInstance && typeof process !== 'undefined' && process.versions?.node) {
    loggerInstance = createLogger();
  }
  return loggerInstance as Logger;
}

/**
 * Default export: exported function only, not eager initialization
 * This prevents SSR hydration mismatch
 */
export const logger = getLogger();

export default logger;
