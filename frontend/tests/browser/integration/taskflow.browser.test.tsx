import React, {JSX} from 'react';
import { describe, expect, it, vi } from 'vitest';
import { cleanup, render } from 'vitest-browser-react';
import TaskForm from '@components/TaskForm';
import { RouterProvider, createRouter, createRootRoute, createMemoryHistory } from '@tanstack/react-router';

// Mock createTask to simulate navigation
vi.mock('@lib/api', (): Record<string, unknown> => ({
  createTask: async () => ({ id: 'task-abc' }),
}));

// Mock navigate by spying on window.history
/**
 * Mount the application with router.
 * @returns {JSX.Element} The React component
 */
function App(): JSX.Element {
  const rootRoute = createRootRoute({ component: TaskForm });
  const router = createRouter({ routeTree: rootRoute, history: createMemoryHistory({ initialEntries: ['/'] }) });
  return <RouterProvider router={router} />;
}

describe('Task submission flow (browser)', () => {
  it('submits and renders form', async () => {
    const screen = await render(<App />);

    await screen.getByRole('textbox', { name: 'Question' }).fill('What is TanStack Start?');
    await screen.getByRole('button', { name: /Submit Question/ }).click();

    await expect.element(screen.getByRole('textbox', { name: 'Question' })).toHaveValue('What is TanStack Start?');
    await cleanup();
  });
});
