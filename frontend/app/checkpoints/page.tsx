'use client'

import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { CheckpointsList } from '@/components/checkpoints/checkpoints-list'

export default function CheckpointsPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Checkpoints</h1>
          <p className="text-muted-foreground">
            Review and approve pending decisions
          </p>
        </div>
        
        <CheckpointsList />
      </div>
    </DashboardLayout>
  )
}