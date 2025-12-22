import { JSX, useEffect, useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getTask, cancelTask } from '@lib/api';
import { WebSocketManager } from '@lib/ws';
import type { StreamEvent } from '@src/types/task';
import AnswerDisplay from './AnswerDisplay';

/**
 * TaskDetail monitors a task and displays real-time updates via WebSocket.
 * @param {object} root0 - Component props
 * @param {string} root0.taskId - The task ID to monitor
 * @returns {JSX.Element} The task detail component
 */
export default function TaskDetail({ taskId }: { taskId: string }): JSX.Element {
  const { data: task, refetch } = useQuery({
    queryKey: ['task', taskId],
    queryFn: () => getTask(taskId),
    refetchInterval: (q) => (q.state.data?.status === 'completed' ? false : 2000),
  });
  const [events, setEvents] = useState<StreamEvent[]>([]);

  const ws = useMemo(
    (): WebSocketManager =>
      new WebSocketManager({
        taskId,
        onEvent: (ev: StreamEvent): void => setEvents((prev) => [...prev, ev]),
        onClose: (): void => void 0,
      }),
    [taskId]
  );

  useEffect(() => {
    ws.connect();
    return (): void => ws.close();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [taskId]);

  /**
   * Cancel the current task and refetch status.
   * @returns {Promise<void>} A promise that resolves when cancellation is complete
   */
  async function onCancel(): Promise<void> {
    await cancelTask(taskId);
    await refetch();
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Task {taskId}</h2>
        <button onClick={onCancel} className="rounded bg-red-600 px-3 py-1">Cancel</button>
      </div>

      <section aria-label="Activity Log" className="rounded border border-neutral-800 p-2">
        <div className="max-h-60 overflow-auto text-sm">
          {events.map((ev) => (
            <div key={ev.ts} className="py-1">
              <span className="text-neutral-400">[{new Date(ev.ts).toLocaleTimeString()}]</span>{' '}
              <span className="font-mono">{ev.type}</span>
            </div>
          ))}
        </div>
      </section>

      {task?.answer && (
        <section aria-label="Answer">
          <AnswerDisplay answer={task.answer} citations={task.citations ?? []} confidence={task.confidence ?? 0} />
        </section>
      )}
    </div>
  );
}
