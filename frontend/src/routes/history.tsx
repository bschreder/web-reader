/**
 * Task history page with filtering, sorting, and search.
 */

import { createFileRoute, Link } from '@tanstack/react-router'
import { useEffect, useState, useMemo } from 'react'
import { listTasks } from '~/lib/api'
import type { Task, TaskStatus } from '~/lib/types'
import { Card, CardHeader, CardTitle, CardContent, Badge, Spinner, Alert, Input, Button } from '~/components/ui'

export const Route = createFileRoute('/history')({
  component: HistoryPage,
})

function HistoryPage() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>('')
  
  // Filters and sorting
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<TaskStatus | 'all'>('all')
  const [sortBy, setSortBy] = useState<'created' | 'status'>('created')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  useEffect(() => {
    let mounted = true
    
    listTasks()
      .then((r) => {
        if (mounted) setTasks(r.tasks || [])
      })
      .catch((err) => {
        if (mounted) setError(err instanceof Error ? err.message : 'Failed to load tasks')
      })
      .finally(() => mounted && setLoading(false))
    
    return () => {
      mounted = false
    }
  }, [])
  
  // Filter and sort tasks
  const filteredAndSortedTasks = useMemo(() => {
    let result = [...tasks]
    
    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      result = result.filter((t) =>
        t.question.toLowerCase().includes(query) ||
        t.task_id.toLowerCase().includes(query)
      )
    }
    
    // Apply status filter
    if (statusFilter !== 'all') {
      result = result.filter((t) => t.status === statusFilter)
    }
    
    // Apply sorting
    result.sort((a, b) => {
      let comparison = 0
      
      if (sortBy === 'created') {
        comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      } else {
        comparison = a.status.localeCompare(b.status)
      }
      
      return sortOrder === 'asc' ? comparison : -comparison
    })
    
    return result
  }, [tasks, searchQuery, statusFilter, sortBy, sortOrder])

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <Spinner size="lg" />
        <p className="mt-4 text-gray-600">Loading task history...</p>
      </div>
    )
  }
  
  if (error) {
    return (
      <Alert variant="danger" title="Error Loading History">
        {error}
      </Alert>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Task History</h2>
        <Link to="/">
          <Button variant="primary" size="sm">
            + New Task
          </Button>
        </Link>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Filters & Search</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Input
              label="Search"
              placeholder="Search questions or task ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              containerClassName="md:col-span-2"
            />
            
            <div>
              <label htmlFor="status-filter" className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                id="status-filter"
                className="block w-full rounded-md border border-gray-300 shadow-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as TaskStatus | 'all')}
              >
                <option value="all">All Statuses</option>
                <option value="created">Created</option>
                <option value="queued">Queued</option>
                <option value="running">Running</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
            
            <div>
              <label htmlFor="sort-by" className="block text-sm font-medium text-gray-700 mb-1">
                Sort By
              </label>
              <div className="flex gap-2">
                <select
                  id="sort-by"
                  className="block w-full rounded-md border border-gray-300 shadow-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as 'created' | 'status')}
                >
                  <option value="created">Date</option>
                  <option value="status">Status</option>
                </select>
                <button
                  type="button"
                  onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                  className="px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
                  aria-label={`Sort ${sortOrder === 'asc' ? 'descending' : 'ascending'}`}
                >
                  {sortOrder === 'asc' ? '↑' : '↓'}
                </button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {filteredAndSortedTasks.length === 0 ? (
        <Alert variant="info">
          {tasks.length === 0
            ? 'No tasks yet. Create your first research task!'
            : 'No tasks match your filters.'}
        </Alert>
      ) : (
        <div className="space-y-3">
          <p className="text-sm text-gray-600">
            Showing {filteredAndSortedTasks.length} of {tasks.length} tasks
          </p>
          {filteredAndSortedTasks.map((task) => (
            <TaskCard key={task.task_id} task={task} />
          ))}
        </div>
      )}
    </div>
  )
}

/**
 * Individual task card in the history list.
 */
function TaskCard({ task }: { task: Task }) {
  const getStatusVariant = (status: TaskStatus) => {
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
  
  return (
    <Card hoverable>
      <CardContent className="py-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <Badge variant={getStatusVariant(task.status)} size="sm">
                {task.status}
              </Badge>
              <span className="text-xs text-gray-500">
                {new Date(task.created_at).toLocaleDateString()} at{' '}
                {new Date(task.created_at).toLocaleTimeString()}
              </span>
            </div>
            <h3 className="font-medium text-gray-900 mb-1 line-clamp-2">
              {task.question}
            </h3>
            {task.seed_url && (
              <p className="text-xs text-gray-500 truncate">
                Seed: <span className="text-blue-600">{task.seed_url}</span>
              </p>
            )}
            {task.duration !== undefined && (
              <p className="text-xs text-gray-500 mt-1">
                Duration: {task.duration}s
              </p>
            )}
          </div>
          <Link to="/tasks/$taskId" params={{ taskId: task.task_id }}>
            <Button variant="secondary" size="sm">
              View Details
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  )
}
