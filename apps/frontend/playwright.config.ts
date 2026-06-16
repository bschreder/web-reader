import type { PlaywrightTestConfig } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';

const parseEnvLine = (line: string): [string, string] | null => {
  const trimmed = line.trim();
  if (!trimmed || trimmed.startsWith('#')) {
    return null;
  }

  const normalized = trimmed.startsWith('export ') ? trimmed.slice(7).trim() : trimmed;
  const eqIndex = normalized.indexOf('=');
  if (eqIndex <= 0) {
    return null;
  }

  const key = normalized.slice(0, eqIndex).trim();
  let value = normalized.slice(eqIndex + 1).trim();

  if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
    value = value.slice(1, -1);
  }

  return [key, value];
};

const applyEnvFile = (filePath: string, override: boolean): void => {
  if (!fs.existsSync(filePath)) {
    return;
  }
  const lines = fs.readFileSync(filePath, 'utf8').split(/\r?\n/);
  for (const line of lines) {
    const parsed = parseEnvLine(line);
    if (!parsed) {
      continue;
    }
    const [key, value] = parsed;
    if (override || process.env[key] === undefined) {
      process.env[key] = value;
    }
  }
};

const loadEnvFile = (): void => {
  // 1. Load the root .env (only fills vars not already set by the shell).
  const baseCandidates = [
    path.resolve(process.cwd(), '.env'),
    path.resolve(process.cwd(), '../../.env'),
  ];
  const envPath = baseCandidates.find((c) => fs.existsSync(c));
  if (envPath) {
    applyEnvFile(envPath, false);
  }

  // 2. Load .env.devcontainer from the same directory as the base .env.
  //    These values override the base .env so devcontainer-specific settings
  //    (e.g. 172.17.0.1 addresses) take precedence.
  if (envPath) {
    const devcontainerEnv = path.join(path.dirname(envPath), '.env.devcontainer');
    applyEnvFile(devcontainerEnv, true);
  }
};

const requireEnv = (name: string): string => {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
};

loadEnvFile();

const defaultBaseURL = 'http://localhost:4173';
const baseURL = process.env.FRONTEND_PUBLIC_URL ?? defaultBaseURL;
process.env.FRONTEND_PUBLIC_URL = baseURL;

const viteApiUrl = requireEnv('VITE_API_URL');

const viteWsUrl = requireEnv('VITE_WS_URL');

const internalApiUrl = requireEnv('INTERNAL_API_URL');

const backendPublicUrl = requireEnv('BACKEND_PUBLIC_URL');

const basePort = Number(new URL(baseURL).port || '80');

// Host-run Playwright dev server cannot resolve compose DNS names like `backend`.
// Derive the replacement host from BACKEND_PUBLIC_URL so that devcontainer
// environments (where localhost may resolve to IPv6 ::1) use the correct host.
// In devcontainers, BACKEND_PUBLIC_URL is overridden by .env.devcontainer.
const backendHost = (() => {
  try {
    return new URL(backendPublicUrl).host;
  } catch {
    return 'localhost';
  }
})();
const internalApiUrlForHost = internalApiUrl.includes('://backend')
  ? internalApiUrl.replace('://backend', `://${backendHost}`)
  : internalApiUrl;

// When FRONTEND_PUBLIC_URL points to a non-loopback host (e.g. 172.17.0.1 in a
// devcontainer), reuse the already-running server instead of starting a new one.
// That server (the Docker frontend container) already has working Docker-DNS proxy
// to the backend, so no new Vite process is needed.
const frontendHost = new URL(baseURL).hostname;
const reuseExistingServer =
  frontendHost !== 'localhost' && frontendHost !== '127.0.0.1';

const config: PlaywrightTestConfig = {
  webServer: {
    command: `npm run dev -- --host 0.0.0.0 --port ${basePort}`,
    url: baseURL,
    env: {
      ...process.env,
      FRONTEND_PUBLIC_URL: baseURL,
      VITE_API_URL: viteApiUrl,
      VITE_WS_URL: viteWsUrl,
      INTERNAL_API_URL: internalApiUrlForHost,
      BACKEND_PUBLIC_URL: backendPublicUrl,
    },
    reuseExistingServer,
    stdout: 'pipe',
    stderr: 'pipe',
  },
  testDir: './tests/e2e',
  retries: 0,
  timeout: 60_000,
  expect: {
    timeout: 30_000,
  },
  fullyParallel: true,    // allow parallel test files
  workers: 2,             // limit workers to reduce resource usage
  reporter: [['list', { forceColors: true }]],
  use: {
    baseURL,
    // headless: true,
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
  },
};

export default config;
