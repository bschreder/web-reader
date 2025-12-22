# Web Reader Frontend (TanStack Start)

- React 19 + Vite + TanStack Router/Query
- Tailwind v4 via `@tailwindcss/vite` (no PostCSS)
- ESLint v9 flat config with React, TypeScript, JSDoc, a11y plugins
- Testing: Vitest (unit + browser) with >80% coverage, Playwright E2E
- Devtools: TanStack React Devtools + Router Devtools enabled in dev

## Scripts

```bash
npm run dev       # Start Vite dev server
npm run build     # Build production assets
npm run preview   # Preview built app
npm run lint      # Lint with ESLint (no warnings allowed)
npm run typecheck # TypeScript type checking
npm run test:unit # Vitest unit tests with coverage
npm run test:browser # Vitest browser tests (headless)
npm run test:e2e  # Playwright E2E tests
```

## Environment

- `VITE_API_URL` (default: http://localhost:8000)
- `VITE_WS_URL` (default: ws://localhost:8000)

## Structure

```
src/
  components/      # UI components
  routes/          # Router pages + layout
  lib/             # API + WebSocket clients
  types/           # Shared type definitions
  entries/         # Client/SSR entries
  styles/          # Tailwind CSS
```
