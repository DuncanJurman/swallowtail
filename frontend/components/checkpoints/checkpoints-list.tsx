'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { checkpointsApi } from '@/services/api'
import { CheckpointCard } from './checkpoint-card'

export function CheckpointsList() {
  const { data: checkpoints, isLoading } = useQuery({
    queryKey: ['checkpoints'],
    queryFn: checkpointsApi.list,
    refetchInterval: 10000, // Poll every 10 seconds
  })

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-6 w-48" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-20 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (!checkpoints || checkpoints.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <p className="text-muted-foreground">No pending checkpoints</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {checkpoints.map((checkpoint) => (
        <CheckpointCard key={checkpoint.id} checkpoint={checkpoint} />
      ))}
    </div>
  )
}