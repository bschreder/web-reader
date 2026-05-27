import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import tsConfigPaths from 'vite-tsconfig-paths';
import { playwright } from '@vitest/browser-playwright';
import { loadEnv } from 'vite';
import path from 'path';

const env = loadEnv('test', path.resolve(__dirname, '..', '..'), '');
const viteApiUrl = env.VITE_API_URL;
const viteWsUrl = env.VITE_WS_URL;

if (!viteApiUrl || !viteWsUrl) {
  throw new Error('Missing required VITE_API_URL or VITE_WS_URL in root .env for test runs.');
}

process.env.INTERNAL_API_URL ??= env.INTERNAL_API_URL || 'http://backend:8000';
process.env.FRONTEND_PUBLIC_URL ??= env.FRONTEND_PUBLIC_URL || 'http://localhost:3000';

// Two test projects: "unit" (node) and "browser" (playwright chromium).
export default defineConfig({
  define: {
    'import.meta.env.VITE_API_URL': JSON.stringify(viteApiUrl),
    'import.meta.env.VITE_WS_URL': JSON.stringify(viteWsUrl),
  },
  plugins: [tsConfigPaths(), react()],
  optimizeDeps: {
    include: ['@tanstack/react-router', '@tanstack/react-router-devtools', 'vitest-browser-react'],
  },
  test: {
    globals: true,
    testTimeout: 10000,
    hookTimeout: 10000,
    pool: 'threads',
    reporters: ['default', 'hanging-process'],
    coverage: {
      provider: 'v8',
      thresholds: {
        branches: 0.8,
        functions: 0.8,
        lines: 0.8,
        statements: 0.8,
      },
      reporter: ['text', 'json', 'html'],
      reportsDirectory: 'coverage',
      include: ['src/**'],
      exclude: [
        'node_modules/',
        'dist/',
        'tests/',
        '**/*.config.{js,ts}',
        '**/routeTree.gen.ts',
        'src/entries/**',
        'src/**/*.css',
      ],
    },
    projects: [
      {
        plugins: [tsConfigPaths(), react()],
        test: {
          name: 'unit',
          include: ['tests/unit/**/*.{test,spec}.ts', 'tests/unit/**/*.{test,spec}.tsx'],
          environment: 'node',
        },
      },
      {
        plugins: [tsConfigPaths(), react()],
        test: {
          name: 'browser',
          include: ['tests/browser/**/*.{test,spec}.tsx'],
          browser: {
            enabled: true,
            provider: playwright(),
            headless: true,
            instances: [
              { browser: 'chromium' },
            ],
          },
        },
      },
    ],
  },
});
