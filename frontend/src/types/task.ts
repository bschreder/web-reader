/**
 * Task type definitions - all inferred from Zod schemas for single source of truth
 * Re-export schema-inferred types for backward compatibility
 */

export type {
  TaskStatus,
  CreateTaskRequest,
  TaskSummary,
  Citation,
  TaskDetail,
  ThinkingEvent,
  ToolCallEvent,
  ToolResultEvent,
  ScreenshotEvent,
  CompleteEvent,
  ErrorEvent,
  StreamEvent,
  CreateTaskResponse,
  ListTasksResponse,
} from '@src/schemas/task.schema';

