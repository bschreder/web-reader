import React from 'react';
import { describe, expect, it, vi } from 'vitest';
import { cleanup, render } from 'vitest-browser-react';
import TaskHistory from '../../../src/components/TaskHistory';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

vi.mock('@lib/api', () => ({
  listTasks: async (): Promise<Record<string, unknown>[]> => [
    { id: '1', question: 'Q1', status: 'completed', createdAt: new Date().toISOString() },
  ],
}));

describe('TaskHistory (browser)', () => {
  it('renders a table with tasks', async () => {
    const qc = new QueryClient();
    const screen = await render(
      <QueryClientProvider client={qc}>
        <TaskHistory />
      </QueryClientProvider>
    );

    await expect.element(screen.getByText('Q1')).toBeVisible();
    await cleanup();
  });
});
