import { defineConfig } from '@tanstack/router-cli/config'

export default defineConfig({
  routesDirectory: './src/routes',
  generatedRouteTree: './src/routeTree.gen.ts',
})
