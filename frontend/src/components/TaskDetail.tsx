/**
 * Task detail component with real-time streaming and enhanced UX.
 */

import { useEffect, useState } from 'react'
import type { AgentEvent, Task } from '~/lib/types'
import { getTask, getScreenshotUrl } from '~/lib/api'
import { connectTaskStream } from '~/lib/websocket'
import { Card, CardHeader, CardTitle, CardContent, Badge, Spinner, Alert, Button } from '~/components/ui'

interface TaskDetailProps {
  /** Task ID to display */
  taskId: string
}

/**
 * Displays task details with real-time streaming updates.
 * 
 * @example
 * ```tsx
 * <TaskDetail taskId="123" />
 * ```
 */
export function TaskDetail({ taskId }: TaskDetailProps) {
  const [task, setTask] = useState<Task | null>(null)
  const [events, setEvents] = useState<AgentEvent[]>([])
  const [answer, setAnswer] = useState<string | undefined>()
  const [citations, setCitations] = useState<Task['citations']>([])
  const [screenshots, setScreenshots] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    let mounted = true
    
    getTask(taskId)
      .then((t) => {
        if (mounted) {
          setTask(t)
          // Pre-populate answer if task is already completed
          if (t.answer) {
            setAnswer(t.answer)
            setCitations(t.citations || [])
          }
        }
      })
      .catch((err) => {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Failed to load task')
        }
      })
      .finally(() => mounted && setLoading(false))
    
    const ws = connectTaskStream(taskId, (evt) => {
      if (!mounted) return
      
      setEvents((prev) => [...prev, evt])
      
      if (evt.type === 'agent:complete') {
        setAnswer(evt.answer)
        setCitations(evt.citations || [])
        setScreenshots(evt.screenshots || [])
        
        // Update task status
        setTask((prev) => prev ? { ...prev, status: 'completed' } : null)
      } else if (evt.type === 'agent:error') {
        setError(evt.error || 'Unknown error occurred')
        setTask((prev) => prev ? { ...prev, status: 'failed' } : null)
      }
    })
    
    return () => {
      mounted = false
      ws.close()
    }
  }, [taskId])

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <Spinner size="lg" />
        <p className="mt-4 text-gray-600">Loading task...</p>
      </div>
    )
  }
  
  if (error) {
    return (
      <Alert variant="danger" title="Error Loading Task">
        {error}
      </Alert>
    )
  }
  
  if (!task) {
    return (
      <Alert variant="warning" title="Task Not Found">
        The requested task could not be found.
      </Alert>
    )
  }

  return (
    <div className="space-y-6" data-testid="task-detail">
      <TaskHeader task={task} />
      <EventLog events={events} isRunning={task.status === 'running'} />
      <AnswerSection
        answer={answer}
        citations={citations}
        screenshots={screenshots}
        taskId={taskId}
        status={task.status}
      />
    </div>
  )
}

/**
 * Task header with status badge and metadata.
 */
function TaskHeader({ task }: { task: Task }) {
  const getStatusVariant = (status: Task['status']) => {
    switch (status) {
      case 'running':
        return 'info' as const
      case 'completed':
        return 'success' as const
      case 'failed':
        return 'danger' as const
      case 'cancelled':
        return 'warning' as const
      default:
        return 'default' as const
    }
  }
  
  const statusVariant = getStatusVariant(task.status)
  
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle>Research Task</CardTitle>
            <p className="mt-2 text-sm text-gray-600">{task.question}</p>
          </div>
          <Badge variant={statusVariant} size="md">
            {task.status}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          {task.seed_url && (
            <div>
              <dt className="font-medium text-gray-500">Seed URL</dt>
              <dd className="mt-1 text-gray-900 truncate">
                <a
                  href={task.seed_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {task.seed_url}
                </a>
              </dd>
            </div>
          )}
          <div>
            <dt className="font-medium text-gray-500">Created</dt>
            <dd className="mt-1 text-gray-900">{new Date(task.created_at).toLocaleString()}</dd>
          </div>
          {task.duration !== undefined && (
            <div>
              <dt className="font-medium text-gray-500">Duration</dt>
              <dd className="mt-1 text-gray-900">{task.duration}s</dd>
            </div>
          )}
        </dl>
      </CardContent>
    </Card>
  )
}

/**
 * Real-time event log with collapsible view.
 */
function EventLog({ events, isRunning }: { events: AgentEvent[]; isRunning: boolean }) {
  const [expanded, setExpanded] = useState(true)
  
  return (
    <Card data-testid="event-log">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CardTitle>Live Events</CardTitle>
            {isRunning && <Spinner size="sm" />}
          </div>
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-sm text-gray-600 hover:text-gray-900"
            aria-expanded={expanded}
            aria-label={expanded ? 'Collapse event log' : 'Expand event log'}
          >
            {expanded ? 'Collapse' : 'Expand'}
          </button>
        </div>
      </CardHeader>
      {expanded && (
        <CardContent>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {events.length === 0 && (
              <p className="text-sm text-gray-500">
                {isRunning ? 'Waiting for agent...' : 'No events recorded'}
              </p>
            )}
            {events.map((e, i) => (
              <EventItem key={i} event={e} index={i} />
            ))}
          </div>
        </CardContent>
      )}
    </Card>
  )
}

/**
 * Individual event item with icon and styling based on type.
 */
function EventItem({ event, index }: { event: AgentEvent; index: number }) {
  const getEventIcon = () => {
    if (event.error) return '❌'
    if (event.type === 'agent:complete') return '✅'
    if (event.type === 'agent:tool_call') return '🔧'
    if (event.type === 'agent:thinking') return '💭'
    return '📝'
  }
  
  const getEventColor = () => {
    if (event.error) return 'text-red-600 bg-red-50'
    if (event.type === 'agent:complete') return 'text-green-600 bg-green-50'
    return 'text-gray-700 bg-gray-50'
  }
  
  return (
    <div className={`p-3 rounded-md text-sm ${getEventColor()}`}>
      <div className="flex items-start gap-2">
        <span className="text-lg leading-none" aria-hidden="true">{getEventIcon()}</span>
        <div className="flex-1 min-w-0">
          <div className="font-mono text-xs mb-1">
            <span className="font-semibold">#{index + 1}</span> {event.type}
            {event.tool && <span className="text-gray-600"> → {event.tool}</span>}
          </div>
          {event.content && (
            <div className="text-sm break-words">{event.content}</div>
          )}
          {event.error && (
            <div className="text-sm font-medium">Error: {event.error}</div>
          )}
        </div>
      </div>
    </div>
  )
}

/**
 * Answer section with copy-to-clipboard and citation management.
 */
function AnswerSection({
  answer,
  citations,
  screenshots,
  taskId,
  status,
}: {
  answer?: string
  citations: Task['citations']
  screenshots: string[]
  taskId: string
  status: Task['status']
}) {
  const [copied, setCopied] = useState(false)
  
  const handleCopy = async () => {
    if (!answer) return
    
    try {
      await navigator.clipboard.writeText(answer)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }
  
  return (
    <Card data-testid="answer-section">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Answer</CardTitle>
          {answer && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCopy}
              aria-label="Copy answer to clipboard"
            >
              {copied ? '✓ Copied!' : '📋 Copy'}
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {!answer && status === 'running' && (
          <div className="flex items-center gap-2 text-gray-600">
            <Spinner size="sm" />
            <span>Agent is researching your question...</span>
          </div>
        )}
        {!answer && status === 'failed' && (
          <Alert variant="danger">
            Task failed to complete. Check the event log for details.
          </Alert>
        )}
        {answer && (
          <div className="prose prose-sm max-w-none">
            <p className="whitespace-pre-line text-gray-700 leading-relaxed" data-testid="answer">
              {answer}
            </p>
          </div>
        )}
        
        {citations.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-3">
              Citations ({citations.length})
            </h4>
            <ul className="space-y-2">
              {citations.map((c, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-blue-600 font-mono text-xs mt-0.5">[{i + 1}]</span>
                  <a
                    href={c.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline text-sm flex-1"
                  >
                    {c.title || c.url}
                    <span className="text-gray-500 block text-xs mt-0.5 truncate">{c.url}</span>
                  </a>
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {screenshots.length > 0 && (
          <div data-testid="screenshots">
            <h4 className="text-sm font-semibold text-gray-900 mb-3">
              Screenshots ({screenshots.length})
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {screenshots.map((_, i) => (
                <div key={i} className="group relative">
                  <img
                    src={getScreenshotUrl(taskId, i)}
                    alt={`Screenshot ${i + 1}`}
                    className="border border-gray-200 rounded-lg object-cover h-40 w-full shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                    loading="lazy"
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-opacity rounded-lg" />
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default TaskDetail
