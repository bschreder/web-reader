import { createFileRoute } from '@tanstack/react-router';
import TaskDetail from '@components/TaskDetail';
import type { JSX } from 'react';
import { getTask } from '@lib/api';
import type { TaskDetail as TaskDetailType } from '@src/schemas/task.schema';

export const Route = createFileRoute('/tasks/$id')({
  // Load task data on server before rendering
  ssr: true,
  // Enable SSR - render component on server with preloaded data
  loader: async ({ params }): Promise<TaskDetailType | null> => {
    try {
      console.debug({ taskId: params.id }, 'Loading task details');
      return await getTask(params.id);
    } catch (error) {
      console.error({ taskId: params.id, error }, 'Failed to load task details');
      return null;
    }
  },
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
