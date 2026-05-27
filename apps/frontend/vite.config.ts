import { defineConfig, loadEnv } from 'vite';
import tsConfigPaths from 'vite-tsconfig-paths';
import { tanstackStart } from '@tanstack/react-start/plugin/vite';
import { devtools } from '@tanstack/devtools-vite';
import tailwindcss from '@tailwindcss/vite';
import viteReact from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig(({ mode }) => {
  // Load env from workspace root (two levels up from apps/frontend)
  const env = loadEnv(mode, path.resolve(__dirname, '..', '..'), '');
  const browserApiBase = env.VITE_API_URL;
  const wsTarget = env.VITE_WS_URL;
  const internalApiTarget = env.INTERNAL_API_URL;
  if (!browserApiBase) {
    throw new Error('Missing required env var VITE_API_URL. Define it in root .env.');
  }
  if (!wsTarget) {
    throw new Error('Missing required env var VITE_WS_URL. Define it in root .env.');
  }
  if (!internalApiTarget) {
    throw new Error('Missing required env var INTERNAL_API_URL. Define it in root .env.');
  }
  
  return {
    define: {
      'import.meta.env.VITE_API_URL': JSON.stringify(browserApiBase),
      'import.meta.env.VITE_WS_URL': JSON.stringify(wsTarget),
    },
    plugins: [
      devtools(),
      tsConfigPaths(),
      tanstackStart(),
      viteReact(), // must come after tanstackStart
      tailwindcss(),
      ].filter(Boolean),
    build: {
      chunkSizeWarningLimit: 700,
      rollupOptions: {
        external: ['node:stream', 'node:stream/web', 'node:async_hooks', 'node:fs', 'node:path'],
        onwarn(warning, defaultHandler) {
          const isTanStackStartUnusedImport =
            warning.message?.includes('@tanstack/start') &&
            warning.message?.includes('imported from external module') &&
            warning.message?.includes('never used');

          if (isTanStackStartUnusedImport || (warning.code === 'UNUSED_EXTERNAL_IMPORT' && warning.id?.includes('@tanstack/start'))) {
            return;
          }

          defaultHandler(warning);
        },
      },
    },
    server: {
      host: '0.0.0.0',
      port: 3000,
      strictPort: true,
      proxy: {
        '/api': {
          target: internalApiTarget,
          changeOrigin: true,
          ws: true,
        },
      },
    },
    preview: {
      host: '0.0.0.0',
      port: 3000,
      strictPort: true,
    },
  };
});
