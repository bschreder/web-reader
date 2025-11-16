# Web Reader Frontend

React-based frontend built with TanStack Start (build-from-scratch via Vite) for the Web Reader AI research assistant.

## Tech Stack

- **Framework**: TanStack Start (React SPA/SSR)
- **Router**: TanStack Router (file-based routing)
- **Styling**: Tailwind CSS
- **TypeScript**: Strict mode with full type safety
- **Build Tool**: Vite (build-from-scratch, no Vinxi)

## Getting Started

### Install Dependencies

```bash
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:3000` by default.

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Environment Variables

Create a `.env.local` file:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## Project Structure

```
frontend/
├── src/
│   ├── routes/              # File-based routes
│   │   ├── __root.tsx       # Root layout
│   │   └── index.tsx        # Home page (task form)
│   ├── components/          # Reusable React components
│   ├── lib/                 # Utilities, API client, types
│   ├── client.tsx           # Client entry point
│   ├── router.tsx           # Router configuration
│   └── styles.css           # Global styles
├── tests/
│   ├── unit/                # Node-based unit tests
│   └── browser/             # Browser (Playwright) component tests
├── public/              # Static assets
├── index.html           # HTML template
├── vite.config.ts       # Vite configuration (TanStack Start plugin)
├── vitest.config.ts     # Vitest config (node + browser projects)
├── tailwind.config.js   # Tailwind CSS configuration
└── tsconfig.json        # TypeScript configuration
```

## Features

- **Real-time Task Monitoring**: WebSocket streaming of agent events
- **Task Management**: Create, view, cancel, and delete tasks
- **History**: Browse past research tasks
- **Responsive Design**: Mobile-friendly UI with Tailwind CSS
- **Type Safety**: Full TypeScript coverage
- **Auto-reconnect**: WebSocket reconnection with exponential backoff

## Development Notes

- Routes are auto-generated from the `src/routes` directory
- API base URL can be configured via environment variables
- WebSocket connections auto-close on task completion
- All API errors are wrapped in typed `APIError` class

## Testing

Run all tests:

```bash
npm test
```

Run only unit tests (Node):

```bash
npm run test:unit
```

Run only browser/component tests (Playwright/Chromium headless):

```bash
npm run test:browser
```
