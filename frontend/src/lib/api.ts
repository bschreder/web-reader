import type { CreateTaskRequest, TaskDetail, TaskSummary } from '@src/types/task';
import {
  CreateTaskRequestSchema,
  CreateTaskResponseSchema,
  TaskDetailSchema,
  ListTasksResponseSchema,
} from '@src/schemas/task.schema';

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

/**
 * Create a new research task.
 * @param {CreateTaskRequest} req - The task creation request
 * @returns {Promise<{id: string}>} A promise resolving to the new task ID
 */
export async function createTask(req: CreateTaskRequest): Promise<{ id: string }> {
  // Validate request data before sending
  const validatedReq = CreateTaskRequestSchema.parse(req);
  
  const res = await fetch(`${API_URL}/api/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(validatedReq),
  });
  if (!res.ok) throw new Error(`Failed to create task: ${res.status}`);
  
  // Validate response data
  const data = await res.json();
  return CreateTaskResponseSchema.parse(data);
}

/**
 * Retrieve task details by ID.
 * @param {string} id - The task ID
 * @returns {Promise<TaskDetail>} A promise resolving to the task details
 */
export async function getTask(id: string): Promise<TaskDetail> {
  const res = await fetch(`${API_URL}/api/tasks/${id}`);
  if (!res.ok) throw new Error(`Failed to get task: ${res.status}`);
  
  // Validate response data
  const data = await res.json();
  return TaskDetailSchema.parse(data);
}

/**
 * Fetch all tasks.
 * @returns {Promise<TaskSummary[]>} A promise resolving to an array of task summaries
 */
export async function listTasks(): Promise<TaskSummary[]> {
  const res = await fetch(`${API_URL}/api/history`);
  if (!res.ok) throw new Error(`Failed to list tasks: ${res.status}`);
  
  // Validate response data
  const data = await res.json();
  return ListTasksResponseSchema.parse(data);
}

/**
 * Cancel a task by ID.
 * @param {string} id - The task ID to cancel
 * @returns {Promise<void>} A promise that resolves when the task is cancelled
 */
export async function cancelTask(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/tasks/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(`Failed to cancel task: ${res.status}`);
}
