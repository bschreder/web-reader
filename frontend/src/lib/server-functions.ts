/**
 * Server-side functions for TanStack Start SSR.
 * These functions run on the server during initial requests and execute on the client
 * during client-side navigation (via React Query).
 */

import { createServerFn } from '@tanstack/react-start/server';
import type { CreateTaskRequest, TaskResponse, TaskListResponse } from '@src/schemas/task.schema';

const API_URL = process.env.VITE_API_URL || 'http://localhost:8000';
const API_TIMEOUT = 30000;

/**
 * Fetch a single task by ID.
 * @param taskId - The task ID
 * @returns Promise with task details
 */
export const getTaskServerFn = createServerFn({
  method: 'GET',
})
  .middleware(async () => undefined)
  .handler(async (taskId: string): Promise<TaskResponse> => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

    try {
      const res = await fetch(`${API_URL}/api/tasks/${taskId}`, {
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!res.ok) {
        throw new Error(
          `Failed to fetch task: ${res.status} ${res.statusText}`
        );
      }

      const data: TaskResponse = await res.json();
      return data;
    } finally {
      clearTimeout(timeoutId);
    }
  });

/**
 * Fetch all tasks with pagination.
 * @param offset - Number of tasks to skip
 * @param limit - Maximum number of tasks to return
 * @returns Promise with task list
 */
export const listTasksServerFn = createServerFn({
  method: 'GET',
})
  .middleware(async () => undefined)
  .handler(
    async (offset: number = 0, limit: number = 100): Promise<TaskListResponse> => {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

      try {
        const url = new URL(`${API_URL}/api/tasks`);
        url.searchParams.set('offset', String(offset));
        url.searchParams.set('limit', String(limit));

        const res = await fetch(url.toString(), {
          signal: controller.signal,
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!res.ok) {
          throw new Error(
            `Failed to fetch tasks: ${res.status} ${res.statusText}`
          );
        }

        const data: TaskListResponse = await res.json();
        return data;
      } finally {
        clearTimeout(timeoutId);
      }
    }
  );

/**
 * Create a new research task.
 * @param req - Task creation request
 * @returns Promise with task ID
 */
export const createTaskServerFn = createServerFn({
  method: 'POST',
})
  .middleware(async () => undefined)
  .handler(
    async (req: CreateTaskRequest): Promise<{ id: string }> => {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

      try {
        const res = await fetch(`${API_URL}/api/tasks`, {
          method: 'POST',
          signal: controller.signal,
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(req),
        });

        if (!res.ok) {
          throw new Error(
            `Failed to create task: ${res.status} ${res.statusText}`
          );
        }

        const data: { id: string } = await res.json();
        return data;
      } finally {
        clearTimeout(timeoutId);
      }
    }
  );

/**
 * Cancel an existing task.
 * @param taskId - The task ID to cancel
 * @returns Promise that resolves when task is cancelled
 */
export const cancelTaskServerFn = createServerFn({
  method: 'DELETE',
})
  .middleware(async () => undefined)
  .handler(async (taskId: string): Promise<void> => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

    try {
      const res = await fetch(`${API_URL}/api/tasks/${taskId}`, {
        method: 'DELETE',
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!res.ok && res.status !== 204) {
        throw new Error(
          `Failed to cancel task: ${res.status} ${res.statusText}`
        );
      }
    } finally {
      clearTimeout(timeoutId);
    }
  });
