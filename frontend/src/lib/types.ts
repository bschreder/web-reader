export type TaskStatus = 'created' | 'queued' | 'running' | 'completed' | 'failed' | 'cancelled'

export interface TaskCreate {
  question: string
  seed_url?: string
  max_depth?: number
  max_pages?: number
  time_budget?: number
}

export interface Citation {
  url: string
  title?: string
  source?: string
  [key: string]: unknown
}

export interface Task {
  task_id: string
  status: TaskStatus
  question: string
  seed_url?: string
  created_at: string
  started_at?: string
  completed_at?: string
  duration?: number
  answer?: string
  citations: Citation[]
  screenshots: string[]
  error?: string
  metadata: Record<string, unknown>
}

export interface AgentEvent {
  type: string
  timestamp?: string
  elapsed?: number
  content?: string
  tool?: string
  args?: Record<string, unknown>
  output?: string
  error?: string
  status?: TaskStatus
  answer?: string
  citations?: Citation[]
  screenshots?: string[]
  metadata?: Record<string, unknown>
}

export interface HealthStatus {
  status: string
  service: string
  version: string
  uptime: number
  tasks: {
    active: number
    total: number
  }
}
