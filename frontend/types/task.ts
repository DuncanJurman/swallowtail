export enum TaskStatus {
  SUBMITTED = 'SUBMITTED',
  QUEUED = 'QUEUED',
  PLANNING = 'PLANNING',
  ASSIGNED = 'ASSIGNED',
  IN_PROGRESS = 'IN_PROGRESS',
  REVIEW = 'REVIEW',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  CANCELLED = 'CANCELLED',
  REJECTED = 'REJECTED',
}

export enum TaskPriority {
  URGENT = 'URGENT',
  NORMAL = 'NORMAL',
  LOW = 'LOW',
}

export interface Task {
  id: string
  instance_id: string
  description: string
  status: TaskStatus
  priority: TaskPriority
  assigned_agents: string[]
  execution_plan?: {
    steps: Array<{
      description: string
      assigned_agent: string
      status: string
    }>
  }
  result?: any
  error_message?: string
  progress_percentage?: number
  created_at: string
  started_at?: string
  completed_at?: string
}

export interface CreateTaskRequest {
  description: string
  priority?: TaskPriority
  auto_execute?: boolean
}