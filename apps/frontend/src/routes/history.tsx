import { createFileRoute } from '@tanstack/react-router';
import TaskHistory from '@components/TaskHistory';
import type { JSX } from 'react';
import { listTasks } from '@lib/api';
import type { TaskSummary } from '@src/types/task';
import { logger } from '@lib/logger';

/**
 * History page component.
 * @returns {JSX.Element} The history page
 */
function HistoryPage(): JSX.Element {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Task History</h1>
      <TaskHistory />
    </div>
  );
}

export const Route = createFileRoute('/history')({
  // Load task history on server before rendering
  ssr: true,
  // Enable SSR - render on server and send HTML to client
  loader: async (): Promise<TaskSummary[]> => {
    try {
      logger?.debug?.('Loading task history');
      return await listTasks();
    } catch (error) {
      logger?.error?.({ error }, 'Failed to load task history');
      return [];
    }
  },
  component: HistoryPage,
});
