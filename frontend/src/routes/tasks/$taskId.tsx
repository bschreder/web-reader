import { createFileRoute } from '@tanstack/react-router'
import { lazy, Suspense } from 'react'
import { Spinner } from '~/components/ui'

// Lazy load TaskDetail component (heavy with WebSocket)
const TaskDetail = lazy(() => import('~/components/TaskDetail').then(m => ({ default: m.TaskDetail })))

export const Route = createFileRoute('/tasks/$taskId')({
  component: TaskDetailPage,
})

function TaskDetailPage() {
  const { taskId } = Route.useParams()
  return (
    <Suspense fallback={<Spinner size="lg" centered />}>
      <TaskDetail taskId={taskId} />
    </Suspense>
  )
}
