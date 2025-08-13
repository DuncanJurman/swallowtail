import { useMutation, useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

interface PostToTikTokParams {
  taskId: string
  title: string
  privacy_level: string
  disable_duet: boolean
  disable_stitch: boolean
  disable_comment: boolean
  account_id?: string
  scheduled_time?: string
}

interface PostStatusResponse {
  publish_id: string
  status: 'PROCESSING' | 'PUBLISH_COMPLETE' | 'FAILED'
  fail_reason?: string
  tiktok_url?: string
  last_checked: string
}

interface TaskDetailResponse {
  task: {
    id: string
    description: string
    status: string
    output_data?: {
      video_url: string
      thumbnail_url: string
      suggested_caption: string
      media_type: string
      duration_seconds: number
      resolution: string
    }
    tiktok_post_status?: string
    tiktok_publish_id?: string
    tiktok_post_url?: string
  }
  planning: {
    steps: Array<{
      id: number
      description: string
      status: string
    }>
  }
  execution_logs: Array<{
    timestamp: string
    agent: string
    action: string
    level: string
    details: string
  }>
  attached_media: Array<{
    id: string
    url: string
    type: string
    caption?: string
  }>
}

// Hook to post video to TikTok
export function usePostToTikTok() {
  return useMutation({
    mutationFn: async ({ taskId, ...data }: PostToTikTokParams) => {
      const response = await apiClient.post(`/tasks/${taskId}/post-to-tiktok`, data)
      return response
    },
    onSuccess: (data) => {
      console.log('Successfully initiated TikTok post:', data)
    },
    onError: (error) => {
      const err = error as { response?: { data?: { detail?: string } }; message?: string }
      console.error('Failed to post to TikTok:', err.response?.data || err.message)
    }
  })
}

// Hook to check post status
export function useTikTokPostStatus(taskId: string, publishId?: string) {
  return useQuery<PostStatusResponse>({
    queryKey: ['tiktok-post-status', taskId, publishId],
    queryFn: async () => {
      const response = await apiClient.get<PostStatusResponse>(`/tasks/${taskId}/post-status`)
      return response
    },
    enabled: !!publishId,
    refetchInterval: (query) => {
      const data = query.state.data
      if (data?.status === 'PROCESSING') {
        return 5000 // Poll every 5 seconds while processing
      }
      return false // Stop polling when complete or failed
    }
  })
}

// Hook to fetch task details
export function useTaskDetail(taskId: string) {
  return useQuery<TaskDetailResponse>({
    queryKey: ['task-detail', taskId],
    queryFn: async () => {
      const response = await apiClient.get<TaskDetailResponse>(`/tasks/${taskId}/detail`)
      return response
    },
    staleTime: 30 * 1000, // Consider data stale after 30 seconds
    refetchOnWindowFocus: false
  })
}

interface TikTokAccountsResponse {
  accounts: Array<{
    id: string
    name: string
    username: string
    isDefault?: boolean
  }>
}

// Hook to fetch TikTok accounts for an instance
export function useTikTokAccounts(instanceId: string) {
  return useQuery<TikTokAccountsResponse>({
    queryKey: ['tiktok-accounts', instanceId],
    queryFn: async () => {
      const response = await apiClient.get<TikTokAccountsResponse>(`/instances/${instanceId}/tiktok-accounts`)
      return response
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: false
  })
}