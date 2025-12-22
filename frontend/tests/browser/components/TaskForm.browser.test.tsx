import React from 'react';
import { describe, expect, it } from 'vitest';
import { createRoot } from 'react-dom/client';
import TaskForm from '../../../src/components/TaskForm';
import { RouterProvider, createRouter, createRootRoute } from '@tanstack/react-router';

/**
 * Mount TaskForm component with required Router provider.
 * @param {HTMLElement} el - The DOM element to mount into
 * @returns {ReturnType<typeof createRoot>} The React root instance
 */
function mount(el: HTMLElement): ReturnType<typeof createRoot> {
  const rootRoute = createRootRoute({ component: () => <TaskForm /> });
  const router = createRouter({ routeTree: rootRoute });
  const root = createRoot(el);
  root.render(<RouterProvider router={router} />);
  return root;
}

describe('TaskForm (browser)', () => {
  it('renders a textarea and button', () => {
    const el = document.createElement('div');
    document.body.appendChild(el);
    const root = mount(el);
    expect(el.querySelector('textarea')).toBeTruthy();
    expect(el.querySelector('button')?.textContent).toContain('Submit');
    root.unmount();
    el.remove();
  });
});
