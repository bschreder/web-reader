/**
 * Server-side functions for TanStack Start SSR.
 * These functions run on the server during initial requests and execute on the client
 * during client-side navigation (via React Query).
 */

import { createServerFn } from '@tanstack/react-start';
import {
  CreateTaskRequestSchema,
} from '@src/schemas/task.schema';
import { z } from 'zod';

const API_URL = process.env.VITE_API_URL || 'http://localhost:8000';
const API_TIMEOUT = 30000;
const TaskIdInputSchema = z.string().min(1);
const ListTasksInputSchema = z
  .object({
    offset: z.number().int().nonnegative().optional(),
    limit: z.number().int().positive().optional(),
  })
  .optional();

/**
 * Fetch a single task by ID.
 * @param taskId - The task ID
 * @returns Promise with task details
 */
export const getTaskServerFn = createServerFn({
  method: 'GET',
})
  .inputValidator(TaskIdInputSchema)
  .handler(async ({ data: taskId }) => {
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

      const data = await res.json();
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
  .inputValidator(ListTasksInputSchema)
  .handler(async ({ data }) => {
      const offset = data?.offset ?? 0;
      const limit = data?.limit ?? 100;
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

        const data = await res.json();
        return data;
      } finally {
        clearTimeout(timeoutId);
      }
    });

/**
 * Create a new research task.
 * @param req - Task creation request
 * @returns Promise with task ID
 */
export const createTaskServerFn = createServerFn({
  method: 'POST',
})
  .inputValidator(CreateTaskRequestSchema)
  .handler(async ({ data: req }) => {
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
    });

/**
 * Cancel an existing task.
 * @param taskId - The task ID to cancel
 * @returns Promise that resolves when task is cancelled
 */
export const cancelTaskServerFn = createServerFn({
  method: 'POST',
})
  .inputValidator(TaskIdInputSchema)
  .handler(async ({ data: taskId }) => {
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
