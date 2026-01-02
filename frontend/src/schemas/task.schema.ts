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
  id: z.string().min(1, 'Invalid task ID'),
  question: z.string(),
  status: TaskStatusSchema,
  createdAt: z.string().datetime('Invalid datetime format'),
});

// Citation validation
export const CitationSchema = z.object({
  title: z.string(),
  url: z.string().url('Invalid citation URL'),
});

// Task detail validation
export const TaskDetailSchema = z.object({
  id: z.string().min(1, 'Invalid task ID'),
  question: z.string(),
  status: TaskStatusSchema,
  startedAt: z.string().datetime('Invalid datetime format').optional(),
  completedAt: z.string().datetime('Invalid datetime format').optional(),
  answer: z.string().optional(),
  citations: z.array(CitationSchema).optional(),
  confidence: z.number().min(0).max(1).optional(),
});

// Stream event base schema
const StreamEventBaseSchema = z.object({
  type: z.enum(['thinking', 'tool_call', 'tool_result', 'screenshot', 'complete', 'error']),
  ts: z.number(),
});

// Individual stream event schemas
export const ThinkingEventSchema = StreamEventBaseSchema.extend({
  type: z.literal('thinking'),
  message: z.string(),
});

export const ToolCallEventSchema = StreamEventBaseSchema.extend({
  type: z.literal('tool_call'),
  tool: z.string(),
  input: z.unknown().optional(),
});

export const ToolResultEventSchema = StreamEventBaseSchema.extend({
  type: z.literal('tool_result'),
  tool: z.string(),
  output: z.unknown().optional(),
});

export const ScreenshotEventSchema = StreamEventBaseSchema.extend({
  type: z.literal('screenshot'),
  imageBase64: z.string(),
});

export const CompleteEventSchema = StreamEventBaseSchema.extend({
  type: z.literal('complete'),
  detail: TaskDetailSchema,
});

export const ErrorEventSchema = StreamEventBaseSchema.extend({
  type: z.literal('error'),
  error: z.string(),
  recoverable: z.boolean().optional(),
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
  id: z.string().min(1, 'Invalid task ID'),
});

export const ListTasksResponseSchema = z.array(TaskSummarySchema);

// Type inference from schemas (optional - can still use existing types)
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
