import { StrictMode } from 'react';
import { hydrateRoot } from 'react-dom/client';
import { StartClient } from '@tanstack/react-start/client';
import { ClientErrorBoundary } from '@components/ErrorBoundary';

hydrateRoot(
  document,
  <StrictMode>
    <ClientErrorBoundary>
      <StartClient />
    </ClientErrorBoundary>
  </StrictMode>
);
