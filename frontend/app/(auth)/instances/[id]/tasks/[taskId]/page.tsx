import { Suspense } from 'react'
import TaskDetailClient from './page-client'

interface TaskDetailPageProps {
  params: Promise<{
    id: string
    taskId: string
  }>
}

export default async function TaskDetailPage({ params }: TaskDetailPageProps) {
  const { id: instanceId, taskId } = await params

  // TODO: In the future, fetch initial task data server-side
  // For now, we'll let the client component handle all data fetching

  return (
    <Suspense fallback={<TaskDetailSkeleton />}>
      <TaskDetailClient instanceId={instanceId} taskId={taskId} />
    </Suspense>
  )
}

function TaskDetailSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-8 bg-secondary rounded w-1/3"></div>
      <div className="grid gap-6">
        <div className="h-64 bg-secondary rounded"></div>
        <div className="h-64 bg-secondary rounded"></div>
        <div className="h-64 bg-secondary rounded"></div>
      </div>
    </div>
  )
}