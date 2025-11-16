import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import tsConfigPaths from 'vite-tsconfig-paths'
import { playwright } from '@vitest/browser-playwright'

// Two test projects: "unit" (node) and "browser" (playwright chromium).
export default defineConfig({
  plugins: [tsConfigPaths(), react()],
  optimizeDeps: {
    include: ['@tanstack/react-router', '@tanstack/react-router-devtools'],
  },
  test: {
    globals: true,
    testTimeout: 10000,
    hookTimeout: 10000,
    pool: 'threads',
    reporters: ['default', 'hanging-process'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'dist/',
        'tests/',
        '**/*.config.{js,ts}',
        '**/routeTree.gen.ts',
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
})
