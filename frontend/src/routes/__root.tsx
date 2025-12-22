import { createRootRoute, Outlet, Link } from '@tanstack/react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TanStackDevtools } from '@tanstack/react-devtools';
import { ReactQueryDevtoolsPanel } from '@tanstack/react-query-devtools';
import { TanStackRouterDevtoolsPanel } from '@tanstack/react-router-devtools';
import { JSX } from 'react';

const qc = new QueryClient();

/**
 * Root layout component for the entire application.
 * @returns {JSX.Element} The root layout with header, main, and devtools
 */
function RootLayout(): JSX.Element {
  const showDevtools = import.meta.env.DEV;
  return (
    <QueryClientProvider client={qc}>
      <div className="min-h-screen bg-neutral-950 text-neutral-100">
        <header className="border-b border-neutral-800">
          <nav className="mx-auto max-w-5xl px-4 py-3 flex gap-4">
            <Link to="/" className="hover:underline">
              Home
            </Link>
            <Link to="/history" className="hover:underline">
              History
            </Link>
          </nav>
        </header>
        <main className="mx-auto max-w-5xl px-4 py-6">
          <Outlet />
        </main>
      </div>
      {showDevtools && (
        <TanStackDevtools
          plugins={[
            {
              name: 'TanStack Query',
              render: <ReactQueryDevtoolsPanel />,
              defaultOpen: false,
            },
            {
              name: 'TanStack Router',
              render: <TanStackRouterDevtoolsPanel />,
              defaultOpen: false,
            },
          ]}
        />
      )}
    </QueryClientProvider>
  );
}

export const Route = createRootRoute({
	component: RootLayout,
});

export default RootLayout;
