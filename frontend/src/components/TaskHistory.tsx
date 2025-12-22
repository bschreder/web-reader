import React, { JSX } from 'react';
import { useQuery } from '@tanstack/react-query';
import { listTasks } from '@lib/api';
import type { TaskSummary } from '@src/types/task';

/**
 * TaskHistory displays a list of all completed and pending tasks.
 * @returns {JSX.Element} The task history component
 */
export default function TaskHistory(): JSX.Element {
  const { data, isLoading, error } = useQuery<TaskSummary[]>({
    queryKey: ['tasks'],
    queryFn: () => listTasks(),
  });

  if (isLoading) return <p>Loading…</p>;
  if (error) return <p role="alert">Failed to load history</p>;

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead className="border-b border-neutral-800">
          <tr>
            <th className="py-2">ID</th>
            <th className="py-2">Question</th>
            <th className="py-2">Status</th>
            <th className="py-2">Created</th>
          </tr>
        </thead>
        <tbody>
          {(data ?? []).map((t) => (
            <tr key={t.id} className="border-b border-neutral-900">
              <td className="py-2 font-mono">{t.id}</td>
              <td className="py-2">{t.question}</td>
              <td className="py-2">{t.status}</td>
              <td className="py-2">{new Date(t.createdAt).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
