import { apiClient } from '@/lib/api-client'
import type {
  WorkflowResponse,
  HumanCheckpoint,
  CheckpointResolution,
  WorkflowStatus,
  ProductIdea,
} from '@/types'

const API_PREFIX = '/api/v1'

// Workflow API
export const workflowApi = {
  start: async (workflowType: string = 'product_launch') => {
    const response = await apiClient.post<WorkflowResponse>(
      `${API_PREFIX}/agents/workflow/start`,
      { workflow_type: workflowType, context: {} }
    )
    return response.data
  },

  getStatus: async () => {
    const response = await apiClient.get<{
      status: WorkflowStatus
      current_product?: ProductIdea
    }>(`${API_PREFIX}/agents/workflow/status`)
    return response.data
  },
}

// Checkpoints API
export const checkpointsApi = {
  list: async () => {
    const response = await apiClient.get<HumanCheckpoint[]>(
      `${API_PREFIX}/checkpoints/`
    )
    return response.data
  },

  get: async (checkpointId: string) => {
    const response = await apiClient.get<{
      checkpoint: HumanCheckpoint
      related_data?: Record<string, any>
    }>(`${API_PREFIX}/checkpoints/${checkpointId}`)
    return response.data
  },

  resolve: async (checkpointId: string, resolution: CheckpointResolution) => {
    const response = await apiClient.post(
      `${API_PREFIX}/checkpoints/${checkpointId}/resolve`,
      resolution
    )
    return response.data
  },
}

// Health API
export const healthApi = {
  check: async () => {
    const response = await apiClient.get<{
      status: string
      redis_connected: boolean
      version: string
    }>('/health')
    return response.data
  },
}