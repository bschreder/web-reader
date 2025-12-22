import React from 'react';
import { describe, expect, it, vi } from 'vitest';
import { createRoot } from 'react-dom/client';
import TaskHistory from '../../../src/components/TaskHistory';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

vi.mock('../../../src/lib/api', () => ({
  listTasks: async (): Promise<Record<string, unknown>[]> => [
    { id: '1', question: 'Q1', status: 'completed', createdAt: new Date().toISOString() },
  ],
}));

describe('TaskHistory (browser)', () => {
  it('renders a table with tasks', async () => {
    const el = document.createElement('div');
    document.body.appendChild(el);
    const root = createRoot(el);
    const qc = new QueryClient();
    root.render(
      <QueryClientProvider client={qc}>
        <TaskHistory />
      </QueryClientProvider>
    );

    // wait a tick for promises
    await Promise.resolve();

    expect(el.textContent).toContain('Q1');
    root.unmount();
    el.remove();
  });
});
