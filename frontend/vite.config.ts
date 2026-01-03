import { defineConfig, loadEnv } from 'vite';
import tsConfigPaths from 'vite-tsconfig-paths';
import { tanstackStart } from '@tanstack/react-start/plugin/vite';
import { devtools } from '@tanstack/devtools-vite';
import tailwindcss from '@tailwindcss/vite';
import viteReact from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig(({ mode }) => {
  // Load env from workspace root (parent directory)
  const env = loadEnv(mode, path.resolve(__dirname, '..'), '');
  
  return {
  define: {
    'import.meta.env.VITE_API_URL': JSON.stringify(env.VITE_API_URL || 'http://localhost:8000'),
    'import.meta.env.VITE_WS_URL': JSON.stringify(env.VITE_WS_URL || 'ws://localhost:8000'),
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
  },
  preview: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: true,
  },
  };
});
