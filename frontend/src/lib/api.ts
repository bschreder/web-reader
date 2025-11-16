import type { Task, TaskCreate, HealthStatus } from './types'

/**
 * Base URL for backend API requests.
 * Falls back to http://localhost:8000 when VITE_API_URL is not provided.
 * @remarks Controlled via environment variable VITE_API_URL.
 */
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * Error type for API failures with optional HTTP status and details.
 * @public
 */
export class APIError extends Error {
  /**
   * Create a new APIError.
   * @param message - Human readable description.
   * @param status - Optional HTTP status code.
   * @param details - Parsed server error payload or low-level error object.
   */
  constructor(
    message: string,
    public status?: number,
    public details?: unknown,
  ) {
    super(message)
    this.name = 'APIError'
  }
}

/**
 * Perform a JSON API request against the backend.
 *
 * @template T Response payload type
 * @param path - Request path beginning with '/'
 * @param options - Fetch options (method, headers, body)
 * @returns Parsed JSON response
 * @throws {@link APIError} When network fails or response is non-2xx
 */
async function apiRequest<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${path}`
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new APIError(
        (errorData as { detail?: string }).detail || `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        errorData,
      )
    }
    return response.json()
  } catch (error) {
    if (error instanceof APIError) throw error
    throw new APIError(error instanceof Error ? error.message : 'Network error', undefined, error)
  }
}

/**
 * Create a new research task.
 * @param data - Task creation payload
 * @returns Newly created {@link Task}
 */
export async function createTask(data: TaskCreate): Promise<Task> {
  return apiRequest<Task>('/api/tasks', { method: 'POST', body: JSON.stringify(data) })
}

/**
 * Retrieve a task by id.
 * @param taskId - Task identifier
 * @returns The {@link Task}
 */
export async function getTask(taskId: string): Promise<Task> {
  return apiRequest<Task>(`/api/tasks/${taskId}`)
}

/**
 * Cancel an existing task.
 * @param taskId - Task identifier
 * @param reason - Optional human-friendly reason
 * @returns Confirmation message
 */
export async function cancelTask(taskId: string, reason?: string): Promise<{ message: string }> {
  return apiRequest(`/api/tasks/${taskId}/cancel`, {
    method: 'POST',
    body: JSON.stringify({ reason: reason || 'Cancelled by user' }),
  })
}

/**
 * Permanently delete a task and its artifacts.
 * @param taskId - Task identifier
 * @returns Confirmation message
 */
export async function deleteTask(taskId: string): Promise<{ message: string }> {
  return apiRequest(`/api/tasks/${taskId}`, { method: 'DELETE' })
}

/**
 * List tasks with optional status filter.
 * @param status - Optional status to filter by
 * @returns Object containing tasks and total count
 */
export async function listTasks(status?: string): Promise<{ tasks: Task[]; total: number }> {
  const params = new URLSearchParams()
  if (status) params.set('status', status)
  return apiRequest(`/api/tasks?${params.toString()}`)
}

/**
 * Retrieve backend health status.
 * @returns {@link HealthStatus}
 */
export async function getHealth(): Promise<HealthStatus> {
  return apiRequest<HealthStatus>('/health')
}

/**
 * Build a direct screenshot URL for a task.
 * @param taskId - Task identifier
 * @param index - Screenshot index
 * @returns Absolute URL to screenshot resource
 */
export function getScreenshotUrl(taskId: string, index: number): string {
  return `${API_BASE_URL}/api/tasks/${taskId}/screenshots/${index}`
}
