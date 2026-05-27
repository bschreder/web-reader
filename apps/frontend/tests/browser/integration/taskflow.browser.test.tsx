import React, {JSX} from 'react';
import { describe, expect, it, vi } from 'vitest';
import { cleanup, render } from 'vitest-browser-react';
import TaskForm from '@components/TaskForm';
import { RouterProvider, createRouter, createRootRoute, createMemoryHistory } from '@tanstack/react-router';
import { AdvancedOptionsProvider } from '@src/lib/advanced-options-context';

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
  return (
    <AdvancedOptionsProvider>
      <RouterProvider router={router} />
    </AdvancedOptionsProvider>
  );
}

describe('Task submission flow (browser)', () => {
  it('submits and renders form', async () => {
    const screen = await render(<App />);

    await screen.getByTestId('question-textarea').fill('What is TanStack Start?');
    await screen.getByTestId('submit-button').click();

    await expect.element(screen.getByTestId('question-textarea')).toHaveValue('What is TanStack Start?');
    await cleanup();
  });
});
