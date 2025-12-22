import type { PlaywrightTestConfig } from '@playwright/test';

const baseURL = process.env.E2E_BASE_URL ?? 'http://localhost:3000';

const config: PlaywrightTestConfig = {
  webServer: {
    command: 'npm run dev',
    url: baseURL,
    reuseExistingServer: true,
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
