/// <reference types="vite/client" />
import { createRootRoute, HeadContent, Outlet, useRouterState } from '@tanstack/react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TanStackDevtools } from '@tanstack/react-devtools';
import { ReactQueryDevtoolsPanel } from '@tanstack/react-query-devtools';
import { TanStackRouterDevtoolsPanel } from '@tanstack/react-router-devtools';
import { JSX } from 'react';
import Header from '@components/Header';
import Footer from '@components/Footer';
import Sidebar from '@components/Sidebar';
import AdvancedOptions from '@components/AdvancedOptions';
import { AdvancedOptionsProvider, useAdvancedOptions } from '@lib/advanced-options-context';
import appCss from '@styles/tailwind.css?url';
import NotFound from '@components/NotFound';

const qc = new QueryClient();

/**
 * Inner layout component that uses the router state.
 * @returns {JSX.Element} The inner layout
 */
function InnerLayout(): JSX.Element {
  const router = useRouterState();
  const currentPath = router.location.pathname;
  const showAdvancedOptions = currentPath === '/';
  const advancedOptions = useAdvancedOptions();

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-neutral-950 via-neutral-900 to-neutral-950 text-neutral-100">
      {/* Header - 25px high, full width */}
      <Header />
      
      {/* Main content - 3 columns */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left sidebar - 15% viewport */}
        <Sidebar />
        
        {/* Center content - fills remaining space */}
        <main className="flex-1 overflow-y-auto px-4 py-6">
          <Outlet />
        </main>
        
        {/* Right sidebar - 35% viewport - only show on home page */}
        {showAdvancedOptions && <AdvancedOptions {...advancedOptions} />}
      </div>
      
      {/* Footer - 25px high, full width, pinned to bottom */}
      <Footer />
    </div>
  );
}

/**
 * Root layout component for the entire application.
 * @returns {JSX.Element} The root layout with header, footer, and 3-column layout
 */
function RootLayout(): JSX.Element {
  const showDevtools = import.meta.env.DEV;
  return (
    <QueryClientProvider client={qc}>
      <AdvancedOptionsProvider>
        <HeadContent />
        <InnerLayout />
      </AdvancedOptionsProvider>
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
  head: () => ({
    meta: [
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { charSet: 'utf-8' },
      { name: 'description', content: 'An advanced AI prompt generator and manager.' },
    ],
    links: [{ rel: 'stylesheet', href: appCss }],
  }),
  notFoundComponent: NotFound,
  component: RootLayout,
});

export default RootLayout;
