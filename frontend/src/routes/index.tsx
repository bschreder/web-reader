import { createFileRoute } from '@tanstack/react-router';
import TaskForm from '@components/TaskForm';
import type { JSX } from 'react';

/**
 * Home page component.
 * @returns {JSX.Element} The home page
 */
function HomePage(): JSX.Element {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Submit Research Task</h1>
      <TaskForm />
    </div>
  );
}

export const Route = createFileRoute('/')({
  component: HomePage,
});
