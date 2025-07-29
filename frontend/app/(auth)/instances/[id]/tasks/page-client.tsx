'use client'

import { useState } from 'react'
import { TaskInput } from '../../../../../components/tasks/task-input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../../../components/ui/card'
import { Badge } from '../../../../../components/ui/badge'
import { Button } from '../../../../../components/ui/button'
import { TaskPriority, TaskStatus } from '../../../../../types/task'
import { 
  CheckCircle, 
  Circle, 
  Clock, 
  XCircle,
  RefreshCw,
  Filter,
  MoreVertical
} from 'lucide-react'

// Mock data
const mockTasks = [
  {
    id: '1',
    description: 'Create Instagram posts for new product launch',
    status: TaskStatus.COMPLETED,
    priority: TaskPriority.URGENT,
    created_at: '2024-01-20T10:00:00Z',
    completed_at: '2024-01-20T10:15:00Z',
    assigned_agents: ['Content Creator', 'Social Media Manager'],
    progress_percentage: 100,
  },
  {
    id: '2',
    description: 'Analyze competitor pricing and suggest adjustments',
    status: TaskStatus.IN_PROGRESS,
    priority: TaskPriority.NORMAL,
    created_at: '2024-01-20T11:00:00Z',
    assigned_agents: ['Market Researcher', 'Pricing Analyst'],
    progress_percentage: 65,
  },
  {
    id: '3',
    description: 'Generate SEO-optimized product descriptions for 10 items',
    status: TaskStatus.QUEUED,
    priority: TaskPriority.LOW,
    created_at: '2024-01-20T12:00:00Z',
    assigned_agents: [],
    progress_percentage: 0,
  },
]

export default function InstanceTasksPageClient({ instanceId }: { instanceId: string }) {
  const [tasks] = useState(mockTasks)
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all')

  const handleTaskSubmit = (taskData: {
    description: string
    priority: TaskPriority
    scheduled_for?: string
  }) => {
    console.log('Submitting task:', taskData)
    // In real app, this would call the API
  }

  const getStatusIcon = (status: TaskStatus) => {
    switch (status) {
      case TaskStatus.COMPLETED:
        return <CheckCircle className="h-4 w-4 text-[--color-green-600]" />
      case TaskStatus.IN_PROGRESS:
        return <RefreshCw className="h-4 w-4 animate-spin text-[--color-blue-600]" />
      case TaskStatus.FAILED:
        return <XCircle className="h-4 w-4 text-[--color-red-600]" />
      case TaskStatus.QUEUED:
        return <Clock className="h-4 w-4 text-[--color-yellow-600]" />
      default:
        return <Circle className="h-4 w-4 text-[--color-gray-400]" />
    }
  }

  const filteredTasks = tasks.filter((task) => {
    if (filter === 'active') {
      return ![TaskStatus.COMPLETED, TaskStatus.FAILED].includes(task.status)
    }
    if (filter === 'completed') {
      return task.status === TaskStatus.COMPLETED
    }
    return true
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Task Management</h1>
        <p className="text-muted-foreground">
          Submit and monitor tasks for your AI agents to execute
        </p>
      </div>

      {/* Task Input */}
      <TaskInput instanceId={instanceId} onSubmit={handleTaskSubmit} />

      {/* Task Queue */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Task Queue</CardTitle>
            <CardDescription>
              Monitor the progress of your submitted tasks
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" className="gap-2">
              <Filter className="h-4 w-4" />
              Filter
            </Button>
            <div className="flex rounded-lg border">
              {['all', 'active', 'completed'].map((filterOption) => (
                <Button
                  key={filterOption}
                  variant={filter === filterOption ? 'default' : 'ghost'}
                  size="sm"
                  className="rounded-none first:rounded-l-lg last:rounded-r-lg"
                  onClick={() => setFilter(filterOption as 'all' | 'active' | 'completed')}
                >
                  {filterOption.charAt(0).toUpperCase() + filterOption.slice(1)}
                </Button>
              ))}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredTasks.map((task) => (
              <div
                key={task.id}
                className="rounded-lg border p-4 transition-colors hover:bg-secondary/50"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-3">
                      {getStatusIcon(task.status)}
                      <p className="font-medium">{task.description}</p>
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <Badge variant={task.priority === TaskPriority.URGENT ? 'destructive' : 'outline'}>
                        {task.priority}
                      </Badge>
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {new Date(task.created_at).toLocaleTimeString()}
                      </span>
                      {task.assigned_agents.length > 0 && (
                        <span>
                          Agents: {task.assigned_agents.join(', ')}
                        </span>
                      )}
                    </div>

                    {task.status === TaskStatus.IN_PROGRESS && (
                      <div className="space-y-1">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">Progress</span>
                          <span className="font-medium">{task.progress_percentage}%</span>
                        </div>
                        <div className="h-2 rounded-full bg-[--color-gray-200]">
                          <div
                            className="h-full rounded-full bg-primary transition-all"
                            style={{ width: `${task.progress_percentage}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}

            {filteredTasks.length === 0 && (
              <div className="py-8 text-center text-muted-foreground">
                No tasks found for the selected filter.
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}