import { createFileRoute } from '@tanstack/react-router';
import TaskDetail from '@components/TaskDetail';
import type { JSX } from 'react';

export const Route = createFileRoute('/tasks/$id')({
  component: TaskDetailPage,
});

/**
 * Task detail page component.
 * @returns {JSX.Element} The task detail page
 */
function TaskDetailPage(): JSX.Element {
  const { id } = Route.useParams();
  return <TaskDetail taskId={id} />;
}
