import { QueryClient } from '@tanstack/react-query';

/**
 * Create a configured React Query client.
 * @returns {QueryClient} A new QueryClient instance with default options
 */
export const createQueryClient = (): QueryClient =>
  new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30_000,
        retry: 1,
        refetchOnWindowFocus: false,
      },
      mutations: {
        retry: 0,
      },
    },
  });
