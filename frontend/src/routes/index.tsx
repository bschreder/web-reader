import { createFileRoute, useRouter } from '@tanstack/react-router'
import { lazy, Suspense } from 'react'
import { createTask } from '~/lib/api'
import type { TaskCreate } from '~/lib/types'
import { Spinner } from '~/components/ui'

// Lazy load TaskForm component
const TaskForm = lazy(() => import('~/components/TaskForm').then(m => ({ default: m.TaskForm })))

export const Route = createFileRoute('/')({
  component: Home,
})

function Home() {
  const router = useRouter()
  const handleSubmit = async (data: TaskCreate) => {
    const task = await createTask(data)
    router.navigate({ to: `/tasks/${task.task_id}` })
  }
  return (
    <div className="space-y-6">
      <Suspense fallback={<Spinner size="lg" centered />}>
        <TaskForm onSubmit={handleSubmit} />
      </Suspense>
    </div>
  )
}
