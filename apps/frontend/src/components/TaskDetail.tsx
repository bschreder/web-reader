import { JSX, useEffect, useMemo, useRef, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';
import { getTask, cancelTask } from '@lib/api';
import { WebSocketManager } from '@lib/ws';
import type { StreamEvent } from '@src/schemas/task.schema';
import AnswerDisplay from './AnswerDisplay';

/**
 * TaskDetail monitors a task and displays real-time updates via WebSocket.
 * @param {object} root0 - Component props
 * @param {string} root0.taskId - The task ID to monitor
 * @returns {JSX.Element} The task detail component
 */
export default function TaskDetail({ taskId }: { taskId: string }): JSX.Element {
  const navigate = useNavigate();
  const { data: task, refetch } = useQuery({
    queryKey: ['task', taskId],
    queryFn: () => getTask(taskId),
    refetchInterval: (q) => (q.state.data?.status === 'completed' ? false : 2000),
  });
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const connectedRef = useRef(false);

  const ws = useMemo(
    (): WebSocketManager =>
      new WebSocketManager({
        taskId,
        onEvent: (ev: StreamEvent): void => {
          console.log('[TaskDetail] WS event received:', ev);
          setEvents((prev) => [...prev, ev]);
        },
        onClose: (): void => {
          console.log('[TaskDetail] WS connection closed');
        },
      }),
    [taskId]
  );

  useEffect(() => {
    console.log('[TaskDetail] Connecting WebSocket for task:', taskId);
    if (!connectedRef.current) {
      connectedRef.current = true; // Avoid double-connect in React strict/dev
      ws.connect();
    }
    return (): void => {
      console.log('[TaskDetail] Cleaning up WebSocket');
      ws.close();
      connectedRef.current = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [taskId]);

  // Debug: Log task data whenever it changes
  useEffect(() => {
    console.log('[TaskDetail] Task data updated:', {
      taskId,
      status: task?.status,
      hasAnswer: !!task?.answer,
      answer: task?.answer,
      citations: task?.citations,
      confidence: task?.confidence,
      eventsCount: events.length,
    });
  }, [task, events.length, taskId]);

  /**
   * Cancel the current task, refetch status, and navigate back to home.
   * @returns {Promise<void>} A promise that resolves when cancellation is complete
   */
  async function onCancel(): Promise<void> {
    await cancelTask(taskId);
    await refetch();
    navigate({ to: '/' });
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Task {taskId}</h2>
        <button onClick={onCancel} className="rounded bg-red-600 px-3 py-1">Cancel</button>
      </div>

      <section aria-label="Activity Log" className="rounded border border-neutral-800 p-2">
        <div className="max-h-60 overflow-auto text-sm">
          {events.map((ev, idx) => (
            <div key={`${ev.timestamp}-${idx}`} className="py-1">
              <span className="text-neutral-400">[{new Date(ev.timestamp).toLocaleTimeString()}]</span>{' '}
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
