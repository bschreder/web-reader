import type { PlaywrightTestConfig } from '@playwright/test';

const defaultBaseURL = 'http://localhost:4173';
const baseURL = process.env.FRONTEND_PUBLIC_URL ?? defaultBaseURL;
process.env.FRONTEND_PUBLIC_URL = baseURL;

const viteApiUrl = process.env.VITE_API_URL;
if (!viteApiUrl) {
  throw new Error('Missing required environment variable: VITE_API_URL');
}

const viteWsUrl = process.env.VITE_WS_URL;
if (!viteWsUrl) {
  throw new Error('Missing required environment variable: VITE_WS_URL');
}

const internalApiUrl = process.env.INTERNAL_API_URL;
if (!internalApiUrl) {
  throw new Error('Missing required environment variable: INTERNAL_API_URL');
}

const backendPublicUrl = process.env.BACKEND_PUBLIC_URL;
if (!backendPublicUrl) {
  throw new Error('Missing required environment variable: BACKEND_PUBLIC_URL');
}

const basePort = Number(new URL(baseURL).port || '80');

// Host-run Playwright dev server cannot resolve compose DNS names like `backend`.
const internalApiUrlForHost = internalApiUrl.includes('://backend')
  ? internalApiUrl.replace('://backend', '://localhost')
  : internalApiUrl;

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
    reuseExistingServer: false,
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
