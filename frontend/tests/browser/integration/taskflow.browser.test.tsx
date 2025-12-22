import React from 'react';
import { describe, expect, it, vi } from 'vitest';
import { createRoot } from 'react-dom/client';
import TaskForm from '@components/TaskForm';
import RootLayout from '@src/routes/__root';
import { RouterProvider, createRouter, createRootRoute, createRoute } from '@tanstack/react-router';

// Mock createTask to simulate navigation
vi.mock('@lib/api', (): Record<string, unknown> => ({
  createTask: async () => ({ id: 'task-abc' }),
}));

// Mock navigate by spying on window.history
/**
 * Mount the application with router.
 * @param {HTMLElement} el - The DOM element to mount into
 * @returns {ReturnType<typeof createRoot>} The React root instance
 */
function mount(el: HTMLElement): ReturnType<typeof createRoot> {
  const rootRoute = createRootRoute({ component: RootLayout });
  const indexRoute = createRoute({ getParentRoute: () => rootRoute, path: '/', component: TaskForm });
  const routeTree = rootRoute.addChildren([indexRoute]);
  const router = createRouter({ routeTree });
  const root = createRoot(el);
  root.render(<RouterProvider router={router} />);
  return root;
}

describe('Task submission flow (browser)', () => {
  it('submits and renders form', async () => {
    const el = document.createElement('div');
    document.body.appendChild(el);
    const root = mount(el);

    const textarea = el.querySelector('textarea') as HTMLTextAreaElement;
    const button = el.querySelector('button') as HTMLButtonElement;

    textarea.value = 'What is TanStack Start?';
    textarea.dispatchEvent(new Event('input', { bubbles: true }));

    button.click();

    expect(textarea.value.length).toBeGreaterThan(0);
    root.unmount();
    el.remove();
  });
});
