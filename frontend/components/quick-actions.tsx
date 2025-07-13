'use client'

import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { workflowApi } from '@/services/api'
import { useToast } from '@/hooks/use-toast'
import { PlayCircle, RefreshCw } from 'lucide-react'

export function QuickActions() {
  const [isStarting, setIsStarting] = useState(false)
  const queryClient = useQueryClient()
  const { toast } = useToast()

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

  const handleStartWorkflow = () => {
    setIsStarting(true)
    startWorkflowMutation.mutate()
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <Button 
          onClick={handleStartWorkflow}
          disabled={isStarting}
          className="w-full"
        >
          {isStarting ? (
            <>
              <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
              Starting...
            </>
          ) : (
            <>
              <PlayCircle className="mr-2 h-4 w-4" />
              Start Product Research
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  )
}