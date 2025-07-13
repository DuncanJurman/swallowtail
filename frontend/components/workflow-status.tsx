'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { workflowApi } from '@/services/api'
import { WorkflowStatus as WorkflowStatusEnum } from '@/types'

const statusColors: Record<WorkflowStatusEnum, string> = {
  [WorkflowStatusEnum.IDLE]: 'secondary',
  [WorkflowStatusEnum.RESEARCHING]: 'default',
  [WorkflowStatusEnum.AWAITING_PRODUCT_APPROVAL]: 'warning',
  [WorkflowStatusEnum.SOURCING]: 'default',
  [WorkflowStatusEnum.AWAITING_SUPPLIER_APPROVAL]: 'warning',
  [WorkflowStatusEnum.CREATING_CONTENT]: 'default',
  [WorkflowStatusEnum.AWAITING_CONTENT_APPROVAL]: 'warning',
  [WorkflowStatusEnum.PREPARING_MARKETING]: 'default',
  [WorkflowStatusEnum.AWAITING_MARKETING_APPROVAL]: 'warning',
  [WorkflowStatusEnum.LAUNCHING]: 'default',
  [WorkflowStatusEnum.LIVE]: 'success',
  [WorkflowStatusEnum.ERROR]: 'destructive',
}

export function WorkflowStatus() {
  const { data, isLoading } = useQuery({
    queryKey: ['workflow-status'],
    queryFn: workflowApi.getStatus,
    refetchInterval: 5000, // Poll every 5 seconds
  })

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Workflow Status</CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-8 w-32" />
        </CardContent>
      </Card>
    )
  }

  const status = data?.status || WorkflowStatusEnum.IDLE
  const badgeVariant = statusColors[status] as any

  return (
    <Card>
      <CardHeader>
        <CardTitle>Workflow Status</CardTitle>
      </CardHeader>
      <CardContent>
        <Badge variant={badgeVariant} className="text-sm">
          {status.replace(/_/g, ' ').toLowerCase()}
        </Badge>
        {data?.current_product && (
          <p className="mt-2 text-sm text-muted-foreground">
            Product: {data.current_product.name}
          </p>
        )}
      </CardContent>
    </Card>
  )
}