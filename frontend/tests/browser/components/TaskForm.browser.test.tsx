import React, {JSX} from 'react';
import { describe, expect, it } from 'vitest';
import { cleanup, render } from 'vitest-browser-react';
import TaskForm from '../../../src/components/TaskForm';
import { RouterProvider, createRouter, createRootRoute, createMemoryHistory } from '@tanstack/react-router';

/**
 * Mount TaskForm component with required Router provider.
 * @returns {JSX.Element} The React component
 */
function App(): JSX.Element {
  const rootRoute = createRootRoute({ component: () => <TaskForm /> });
  const router = createRouter({ routeTree: rootRoute, history: createMemoryHistory({ initialEntries: ['/'] }) });
  return <RouterProvider router={router} />;
}

describe('TaskForm (browser)', () => {
  it('renders a textarea and button', async () => {
    const screen = await render(<App />);
    await expect.element(screen.getByRole('textbox', { name: 'Question' })).toBeVisible();
    await expect.element(screen.getByRole('button', { name: /Submit Question/ })).toBeVisible();
    await cleanup();
  });
});
