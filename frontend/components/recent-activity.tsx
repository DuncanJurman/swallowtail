'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useWebSocket } from '@/providers/websocket-provider'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'

interface ActivityItem {
  id: string
  timestamp: Date
  type: 'agent' | 'checkpoint' | 'workflow'
  message: string
}

export function RecentActivity() {
  const [activities, setActivities] = useState<ActivityItem[]>([])
  const { subscribe, unsubscribe } = useWebSocket()

  useEffect(() => {
    const handleActivity = (data: any) => {
      const newActivity: ActivityItem = {
        id: Date.now().toString(),
        timestamp: new Date(),
        type: data.type || 'agent',
        message: data.message || 'Activity logged',
      }
      
      setActivities((prev) => [newActivity, ...prev].slice(0, 10))
    }

    subscribe('activity', handleActivity)
    subscribe('agent:status', handleActivity)
    subscribe('workflow:update', handleActivity)

    return () => {
      unsubscribe('activity', handleActivity)
      unsubscribe('agent:status', handleActivity)
      unsubscribe('workflow:update', handleActivity)
    }
  }, [subscribe, unsubscribe])

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[200px]">
          {activities.length === 0 ? (
            <p className="text-sm text-muted-foreground">No recent activity</p>
          ) : (
            <div className="space-y-2">
              {activities.map((activity) => (
                <div key={activity.id} className="flex items-start gap-2 text-sm">
                  <Badge variant="outline" className="text-xs">
                    {activity.type}
                  </Badge>
                  <div className="flex-1">
                    <p>{activity.message}</p>
                    <p className="text-xs text-muted-foreground">
                      {activity.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  )
}