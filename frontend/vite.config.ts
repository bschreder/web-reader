import { defineConfig } from 'vite';
import tsConfigPaths from 'vite-tsconfig-paths';
import { tanstackStart } from '@tanstack/react-start/plugin/vite';
import { devtools } from '@tanstack/devtools-vite';
import tailwindcss from '@tailwindcss/vite';
import viteReact from '@vitejs/plugin-react';

const isDev = process.env.NODE_ENV === 'development';

export default defineConfig({
  plugins: [
    isDev && devtools(),
    tsConfigPaths(),
    tanstackStart(),
    tailwindcss(),
    viteReact(), // must come after tanstackStart
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
    port: 3000,
    strictPort: true,
  },
  preview: {
    port: 3000,
    strictPort: true,
  },
});
