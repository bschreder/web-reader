import pino from "pino";
import fs from "node:fs";
import path from "node:path";

// Resolve env from Vite or Node
const LOG_LEVEL = (
  (import.meta as any)?.env?.LOG_LEVEL ?? process.env.LOG_LEVEL ?? "info"
) as pino.LevelWithSilent;

// Always default to writing to console and file
const LOG_TARGET = ((import.meta as any)?.env?.LOG_TARGET ?? process.env.LOG_TARGET ?? "both") as
  | "console"
  | "file"
  | "both";

const dateStr = new Date().toISOString().slice(0, 10).replace(/-/g, "");
const defaultLogFile = `logs/log-frontend-${dateStr}.json`;
const LOG_FILE = ((import.meta as any)?.env?.LOG_FILE ?? process.env.LOG_FILE ?? defaultLogFile) as string;

// Ensure destination directory exists if writing to file
try {
  const dir = path.dirname(LOG_FILE);
  fs.mkdirSync(dir, { recursive: true });
} catch {}

const isDev = process.env.NODE_ENV !== "production";

const targets: any[] = [];

// Console output
if (LOG_TARGET === "console" || LOG_TARGET === "both") {
  if (isDev) {
    targets.push({
      target: "pino-pretty",
      options: {
        colorize: true,
        singleLine: false,
        translateTime: "SYS:standard",
      },
      level: LOG_LEVEL,
    });
  } else {
    // In production, default to JSON to stderr
    targets.push({
      target: "pino/file",
      options: { destination: 2 }, // 2 = stderr fd
      level: LOG_LEVEL,
    });
  }
}

// JSON file output (always JSON)
if (LOG_TARGET === "file" || LOG_TARGET === "both") {
  targets.push({
    target: "pino/file",
    options: { destination: LOG_FILE, mkdir: true },
    level: LOG_LEVEL,
  });
}

export const logger = pino(
  { level: LOG_LEVEL },
  targets.length ? pino.transport({ targets }) : undefined
);
