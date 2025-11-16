import { defineConfig } from 'vite'
import tsConfigPaths from 'vite-tsconfig-paths'
import { tanstackStart } from '@tanstack/react-start/plugin/vite'
import tailwindcss from '@tailwindcss/vite'
import viteReact from '@vitejs/plugin-react'

export default defineConfig({
  server: {
    port: 3000,
    host: true,
  },
  plugins: [
    tsConfigPaths(),
    tanstackStart(),
    tailwindcss(),
    viteReact(), // must come after tanstackStart
  ],
})
