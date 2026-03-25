import * as z from 'zod';

/**
 * Zod schemas for runtime validation of task-related data.
 * Provides type-safe parsing and validation of API responses and user input.
 */

// Task status validation
export const TaskStatusSchema = z.enum([
  'created',
  'queued',
  'running',
  'completed',
  'failed',
  'cancelled',
]);

// Search engine validation
export const SearchEngineSchema = z.enum([
  'duckduckgo',
  'bing',
  'google',
  'custom',
]);

// Create task request validation
export const CreateTaskRequestSchema = z.object({
  question: z.string().min(1, 'Question is required'),
  seedUrl: z.string().url('Must be a valid URL').optional(),
  maxDepth: z.number().int().positive().optional(),
  maxPages: z.number().int().positive().optional(),
  timeBudget: z.number().int().positive().optional(),
  // UC-01: Web Search parameters
  searchEngine: SearchEngineSchema.optional(),
  maxResults: z.number().int().positive().optional(),
  safeMode: z.boolean().optional(),
  // UC-02: Link following parameters
  sameDomainOnly: z.boolean().optional(),
  allowExternalLinks: z.boolean().optional(),
});

// Task summary validation
export const TaskSummarySchema = z.object({
  taskId: z.string().min(1, 'Invalid task ID'),
  question: z.string().min(1, 'Question is required'),
  status: TaskStatusSchema,
  createdAt: z.coerce.date().optional(),
});

// Citation validation
export const CitationSchema = z.object({
  title: z.string(),
  url: z.url('Invalid citation URL'),
  excerpt: z.string().optional(),
});

// Task detail validation
export const TaskDetailSchema = z.object({
  taskId: z.string().min(1, 'Invalid task ID'),
  question: z.string().min(1, 'Question is required'),
  status: TaskStatusSchema,
  seedUrl: z.url().nullable().optional(),
  createdAt: z.coerce.date().optional(),
  startedAt: z.coerce.date().nullable().optional(),
  completedAt: z.coerce.date().nullable().optional(),
  duration: z.number().nullable().optional(),
  answer: z.string().nullable().optional(),
  citations: z.array(CitationSchema).optional(),
  screenshots: z.array(z.string()).optional(),
  confidence: z.number().min(0).max(1).nullable().optional(),
  error: z.string().nullable().optional(),
  metadata: z.record(z.string(), z.unknown()).optional(),
});

// Stream event base schema
export const StreamEventBaseSchema = z.object({
  type: z.enum(['agent:thinking', 'agent:tool_call', 'agent:tool_result', 'agent:screenshot', 'agent:complete', 'agent:error']),
  taskId: z.string(),
  timestamp: z.coerce.date(),
});

// Individual stream event schemas
export const ThinkingEventSchema = StreamEventBaseSchema.extend({
  type: z.literal('agent:thinking'),
  content: z.string().optional(),
  message: z.string().optional(),
  metadata: z.unknown().optional(),
});

export const ToolCallEventSchema = StreamEventBaseSchema.extend({
  type: z.literal('agent:tool_call'),
  tool: z.string(),
  args: z.unknown().optional(),
  input: z.unknown().optional(),
  metadata: z.unknown().optional(),
});

export const ToolResultEventSchema = StreamEventBaseSchema.extend({
  type: z.literal('agent:tool_result'),
  tool: z.string(),
  result: z.unknown().optional(),
  output: z.unknown().optional(),
  success: z.boolean().optional(),
  metadata: z.unknown().optional(),
});

export const ScreenshotEventSchema = StreamEventBaseSchema.extend({
  type: z.literal('agent:screenshot'),
  imageUrl: z.string().optional(),
  imageBase64: z.string().optional(),
  fullPage: z.boolean().optional(),
  metadata: z.unknown().optional(),
});

export const CompleteEventSchema = StreamEventBaseSchema.extend({
  type: z.literal('agent:complete'),
  answer: z.string().optional(),
  citations: z.array(CitationSchema).optional(),
  duration: z.number().optional(),
  confidence: z.number().min(0).max(1).optional(),
  metadata: z.unknown().optional(),
});

export const ErrorEventSchema = StreamEventBaseSchema.extend({
  type: z.literal('agent:error'),
  error: z.string(),
  recoverable: z.boolean().optional(),
  metadata: z.unknown().optional(),
});

// Discriminated union for stream events
export const StreamEventSchema = z.discriminatedUnion('type', [
  ThinkingEventSchema,
  ToolCallEventSchema,
  ToolResultEventSchema,
  ScreenshotEventSchema,
  CompleteEventSchema,
  ErrorEventSchema,
]);

// API response schemas
export const CreateTaskResponseSchema = z.object({
  taskId: z.string().min(1, 'Invalid task ID'),
});

export const ListTasksResponseSchema = z.array(TaskSummarySchema);

// Additional response schemas for server functions
export const TaskResponseSchema = TaskDetailSchema;
export const TaskListResponseSchema = z.object({
  tasks: z.array(TaskSummarySchema),
  total: z.number().optional(),
});

// Type inference from schemas
export type TaskStatus = z.infer<typeof TaskStatusSchema>;
export type SearchEngine = z.infer<typeof SearchEngineSchema>;
export type CreateTaskRequest = z.infer<typeof CreateTaskRequestSchema>;
export type TaskSummary = z.infer<typeof TaskSummarySchema>;
export type Citation = z.infer<typeof CitationSchema>;
export type TaskDetail = z.infer<typeof TaskDetailSchema>;
export type ThinkingEvent = z.infer<typeof ThinkingEventSchema>;
export type ToolCallEvent = z.infer<typeof ToolCallEventSchema>;
export type ToolResultEvent = z.infer<typeof ToolResultEventSchema>;
export type ScreenshotEvent = z.infer<typeof ScreenshotEventSchema>;
export type CompleteEvent = z.infer<typeof CompleteEventSchema>;
export type ErrorEvent = z.infer<typeof ErrorEventSchema>;
export type StreamEvent = z.infer<typeof StreamEventSchema>;
export type CreateTaskResponse = z.infer<typeof CreateTaskResponseSchema>;
export type ListTasksResponse = z.infer<typeof ListTasksResponseSchema>;
export type TaskResponse = z.infer<typeof TaskResponseSchema>;
export type TaskListResponse = z.infer<typeof TaskListResponseSchema>;
