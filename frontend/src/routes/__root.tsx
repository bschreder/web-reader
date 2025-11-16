/// <reference types="vite/client" />
import type { ReactNode } from 'react'
import { Outlet, HeadContent, Scripts, createRootRoute, Link } from '@tanstack/react-router'
import { lazy, Suspense } from 'react'

// Lazy load DevTools only in development
const TanStackRouterDevtools =
  import.meta.env.MODE === 'production'
    ? () => null
    : lazy(() =>
        import('@tanstack/react-router-devtools').then((res) => ({
          default: res.TanStackRouterDevtools,
        })),
      )

export const Route = createRootRoute({
  head: () => ({
    meta: [
      { charSet: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { title: 'Web Reader' },
    ],
  }),
  notFoundComponent: () => (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-4xl font-bold text-gray-900 mb-4">404 - Not Found</h1>
      <p className="text-gray-600 mb-8">The page you're looking for doesn't exist.</p>
      <Link to="/" className="btn-primary">Go Home</Link>
    </div>
  ),
  component: RootComponent,
})

function RootComponent() {
  return (
    <RootDocument>
      <Layout>
        <Outlet />
      </Layout>
    </RootDocument>
  )
}

function RootDocument({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <head>
        <HeadContent />
      </head>
      <body className="min-h-screen bg-gray-50 text-gray-900">
        {children}
        <Scripts />
      </body>
    </html>
  )
}

function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="flex flex-col min-h-screen">
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">🔍 Web Reader</h1>
            <p className="text-sm text-gray-500">AI-powered web research assistant</p>
          </div>
          <nav className="flex space-x-4 text-sm">
            <Link to="/" className="text-gray-600 hover:text-gray-900">
              New Task
            </Link>
            <Link to="/history" className="text-gray-600 hover:text-gray-900">
              History
            </Link>
          </nav>
        </div>
      </header>
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
      <footer className="bg-white border-t border-gray-200 text-center text-xs py-4 text-gray-500">
        Web Reader v0.1.0 • TanStack Start & LangChain
      </footer>
      <Suspense fallback={null}>
        <TanStackRouterDevtools />
      </Suspense>
    </div>
  )
}
