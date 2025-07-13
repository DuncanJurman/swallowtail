'use client'

import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { WorkflowStatus } from '@/components/workflow-status'
import { QuickActions } from '@/components/quick-actions'
import { RecentActivity } from '@/components/recent-activity'

export default function HomePage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            Monitor and control your autonomous e-commerce agents
          </p>
        </div>
        
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <WorkflowStatus />
          <QuickActions />
          <RecentActivity />
        </div>
      </div>
    </DashboardLayout>
  )
}