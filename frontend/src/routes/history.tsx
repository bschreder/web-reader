import { createFileRoute } from '@tanstack/react-router';
import TaskHistory from '@components/TaskHistory';
import type { JSX } from 'react';

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
  component: HistoryPage,
});
