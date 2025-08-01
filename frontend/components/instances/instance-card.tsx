import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { Badge } from '../ui/badge'
import { Instance, InstanceType } from '../../types/instance'
import { Building2, Globe, MoreVertical, Activity, Clock, Users } from 'lucide-react'
import Link from 'next/link'
import { cn } from '../../lib/utils'

interface InstanceCardProps {
  instance: Instance
  metrics?: {
    activeTasks: number
    completedToday: number
    activeAgents: number
  }
}

export function InstanceCard({ instance, metrics }: InstanceCardProps) {
  const isEcommerce = instance.type === InstanceType.ECOMMERCE
  const Icon = isEcommerce ? Building2 : Globe

  return (
    <Card className="group relative overflow-hidden transition-all hover:shadow-lg">
      {/* Status indicator */}
      <div
        className={cn(
          'absolute left-0 top-0 h-full w-1',
          instance.is_active ? 'bg-green-500' : 'bg-gray-300'
        )}
      />

      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div
              className={cn(
                'flex h-10 w-10 items-center justify-center rounded-lg',
                isEcommerce ? 'bg-[--color-primary]/10 text-[--color-primary]' : 'bg-[--color-secondary]/10 text-[--color-secondary]'
              )}
            >
              <Icon className="h-5 w-5" />
            </div>
            <div>
              <CardTitle className="text-lg">{instance.name}</CardTitle>
              <CardDescription className="text-xs">
                {instance.description || 'No description'}
              </CardDescription>
            </div>
          </div>
          <Button variant="ghost" size="icon" className="h-8 w-8">
            <MoreVertical className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Instance type badge */}
        <div className="flex items-center gap-2">
          <Badge variant={isEcommerce ? 'default' : 'secondary'} className="text-xs">
            {isEcommerce ? 'Ecommerce' : 'Social Media'}
          </Badge>
          {instance.platform_connections && Object.keys(instance.platform_connections).length > 0 && (
            <Badge variant="outline" className="text-xs">
              {Object.keys(instance.platform_connections).length} platforms
            </Badge>
          )}
        </div>

        {/* Metrics */}
        {metrics && (
          <div className="grid grid-cols-3 gap-2 text-center">
            <div className="space-y-1">
              <Activity className="mx-auto h-4 w-4 text-[--color-muted-foreground]" />
              <p className="text-2xl font-semibold">{metrics.activeTasks}</p>
              <p className="text-xs text-[--color-muted-foreground]">Active</p>
            </div>
            <div className="space-y-1">
              <Clock className="mx-auto h-4 w-4 text-[--color-muted-foreground]" />
              <p className="text-2xl font-semibold">{metrics.completedToday}</p>
              <p className="text-xs text-[--color-muted-foreground]">Today</p>
            </div>
            <div className="space-y-1">
              <Users className="mx-auto h-4 w-4 text-[--color-muted-foreground]" />
              <p className="text-2xl font-semibold">{metrics.activeAgents}</p>
              <p className="text-xs text-[--color-muted-foreground]">Agents</p>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-2 pt-2">
          <Link href={`/instances/${instance.id}/settings`} className="flex-1">
            <Button variant="outline" size="sm" className="w-full">
              Settings
            </Button>
          </Link>
          <Link href={`/instances/${instance.id}/tasks`} className="flex-1">
            <Button size="sm" className="w-full">
              Manage Tasks
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  )
}