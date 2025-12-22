import React from 'react';
import ReactDOM from 'react-dom/client';
import { createRouter, RouterProvider } from '@tanstack/react-router';
import { QueryClientProvider } from '@tanstack/react-query';
import { createQueryClient } from '@lib/query-client';
import '@styles/tailwind.css';
import { routeTree } from '@src/routeTree.gen';

const rootElement = document.getElementById('app');
if (!rootElement) throw new Error('Root element not found');

if (!rootElement.innerHTML) {
  const root = ReactDOM.createRoot(rootElement);
  const router = createRouter({ routeTree });
  const queryClient = createQueryClient();
  root.render(
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  );
}
