import './tailwind-setup';
import '@styles/tailwind.css';
import React from 'react';
import { createRoot } from 'react-dom/client';
import {  RouterProvider } from '@tanstack/react-router';
import { QueryClientProvider } from '@tanstack/react-query';
import { getRouter } from '@src/router';
import { createQueryClient } from '@lib/query-client';

const router = getRouter();
const queryClient = createQueryClient();

const el = document.getElementById('app')!;
createRoot(el).render(
  <QueryClientProvider client={queryClient}>
    <RouterProvider router={router} />
  </QueryClientProvider>
);
