import { createFileRoute } from '@tanstack/react-router';
import TaskForm from '@components/TaskForm';
import type { JSX } from 'react';

/**
 * Home page component with title.
 * @returns {JSX.Element} The home page
 */
function HomePage(): JSX.Element {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <svg data-testid="home-hero-icon" className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
          Submit Research Task
        </h1>
      </div>
      <TaskForm />
    </div>
  );
}

export const Route = createFileRoute('/')({
  component: HomePage,
});
