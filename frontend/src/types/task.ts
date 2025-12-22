export type TaskStatus = 'queued' | 'running' | 'completed' | 'failed' | 'cancelled'

export interface CreateTaskRequest {
  question: string
  seedUrl?: string
  options?: {
    depth?: number
    pages?: number
    timeBudgetSec?: number
  }
}

export interface TaskSummary {
  id: string
  question: string
  status: TaskStatus
  createdAt: string
}

export interface TaskDetail {
  id: string
  question: string
  status: TaskStatus
  startedAt?: string
  completedAt?: string
  answer?: string
  citations?: Array<{ title: string; url: string }>
  confidence?: number
}

export interface StreamEventBase {
  type: 'thinking' | 'tool_call' | 'tool_result' | 'screenshot' | 'complete' | 'error'
  ts: number
}

export interface ThinkingEvent extends StreamEventBase {
  type: 'thinking'
  message: string
}

export interface ToolCallEvent extends StreamEventBase {
  type: 'tool_call'
  tool: string
  input?: unknown
}

export interface ToolResultEvent extends StreamEventBase {
  type: 'tool_result'
  tool: string
  output?: unknown
}

export interface ScreenshotEvent extends StreamEventBase {
  type: 'screenshot'
  imageBase64: string
}

export interface CompleteEvent extends StreamEventBase {
  type: 'complete'
  detail: TaskDetail
}

export interface ErrorEvent extends StreamEventBase {
  type: 'error'
  error: string
  recoverable?: boolean
}

export type StreamEvent =
  | ThinkingEvent
  | ToolCallEvent
  | ToolResultEvent
  | ScreenshotEvent
  | CompleteEvent
  | ErrorEvent
