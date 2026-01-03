import { createRouter } from '@tanstack/react-router';
import { routeTree } from '@src/routeTree.gen';
import { PrettyErrorBoundary } from '@components/ErrorBoundary';

/**
 * Create a new router instance (required by TanStack Start).
 * @returns {ReturnType<typeof createRouter>} The configured router instance
 */
export function getRouter(): ReturnType<typeof createRouter> {
  return createRouter({
    routeTree,
    defaultErrorComponent: PrettyErrorBoundary,
    scrollRestoration: true,
  });
}

declare module '@tanstack/react-router' {
  interface Register {
    router: ReturnType<typeof getRouter>
  }
}
