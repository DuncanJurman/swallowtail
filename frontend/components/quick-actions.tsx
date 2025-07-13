'use client'

import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { workflowApi } from '@/services/api'
import { useToast } from '@/hooks/use-toast'
import { PlayCircle, RefreshCw, XCircle } from 'lucide-react'

export function QuickActions() {
  const [isStarting, setIsStarting] = useState(false)
  const [isCancelling, setIsCancelling] = useState(false)
  const queryClient = useQueryClient()
  const { toast } = useToast()

  // Get current workflow status
  const { data: workflowStatus } = useQuery({
    queryKey: ['workflow-status'],
    queryFn: workflowApi.getStatus,
    refetchInterval: 5000,
  })

  // Check if workflow is active
  const isWorkflowActive = workflowStatus?.status && 
    !['idle', 'error', 'completed'].includes(workflowStatus.status)

  const startWorkflowMutation = useMutation({
    mutationFn: () => workflowApi.start(),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['workflow-status'] })
      queryClient.invalidateQueries({ queryKey: ['checkpoints'] })
      
      if (data.success) {
        toast({
          title: 'Workflow Started',
          description: 'Product research workflow has been initiated',
        })
      } else {
        toast({
          title: 'Error',
          description: data.error || 'Failed to start workflow',
          variant: 'destructive',
        })
      }
      setIsStarting(false)
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to start workflow',
        variant: 'destructive',
      })
      setIsStarting(false)
    },
  })

  const cancelWorkflowMutation = useMutation({
    mutationFn: () => workflowApi.cancel(),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['workflow-status'] })
      queryClient.invalidateQueries({ queryKey: ['checkpoints'] })
      
      if (data.success) {
        toast({
          title: 'Workflow Cancelled',
          description: 'The workflow has been cancelled successfully',
        })
      } else {
        toast({
          title: 'Error',
          description: data.error || 'Failed to cancel workflow',
          variant: 'destructive',
        })
      }
      setIsCancelling(false)
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to cancel workflow',
        variant: 'destructive',
      })
      setIsCancelling(false)
    },
  })

  const handleStartWorkflow = () => {
    setIsStarting(true)
    startWorkflowMutation.mutate()
  }

  const handleCancelWorkflow = () => {
    setIsCancelling(true)
    cancelWorkflowMutation.mutate()
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <Button 
          onClick={handleStartWorkflow}
          disabled={isStarting || isWorkflowActive}
          className="w-full"
          title={isWorkflowActive ? `Workflow is currently ${workflowStatus?.status}` : undefined}
        >
          {isStarting ? (
            <>
              <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
              Starting...
            </>
          ) : isWorkflowActive ? (
            <>
              <RefreshCw className="mr-2 h-4 w-4" />
              Workflow {workflowStatus?.status}
            </>
          ) : (
            <>
              <PlayCircle className="mr-2 h-4 w-4" />
              Start Product Research
            </>
          )}
        </Button>
        {isWorkflowActive && (
          <>
            <Button
              onClick={handleCancelWorkflow}
              disabled={isCancelling}
              variant="destructive"
              className="w-full"
            >
              {isCancelling ? (
                <>
                  <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                  Cancelling...
                </>
              ) : (
                <>
                  <XCircle className="mr-2 h-4 w-4" />
                  Cancel Workflow
                </>
              )}
            </Button>
            <p className="text-sm text-muted-foreground text-center">
              A workflow is currently active. Please wait for it to complete or cancel it.
            </p>
          </>
        )}
      </CardContent>
    </Card>
  )
}