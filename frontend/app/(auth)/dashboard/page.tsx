import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card'
import { Button } from '../../../components/ui/button'
import { Plus, TrendingUp, Activity, Users, DollarSign } from 'lucide-react'
import Link from 'next/link'
import { cn } from '@/lib/utils'

// Mock data - will be replaced with API calls
const stats = [
  {
    title: 'Active Instances',
    value: '3',
    description: '2 Ecommerce, 1 Social',
    icon: Activity,
    trend: '+2 this month',
  },
  {
    title: 'Tasks Completed',
    value: '147',
    description: 'Last 30 days',
    icon: TrendingUp,
    trend: '+23% from last month',
  },
  {
    title: 'Active Agents',
    value: '18',
    description: 'Across all instances',
    icon: Users,
    trend: '6 agents per instance',
  },
  {
    title: 'Revenue Generated',
    value: '$12,435',
    description: 'This month',
    icon: DollarSign,
    trend: '+15% from last month',
  },
]

const recentActivity = [
  {
    id: 1,
    instance: 'TechGadgets Store',
    task: 'Generated product descriptions for 5 items',
    time: '2 hours ago',
    status: 'completed',
  },
  {
    id: 2,
    instance: 'Fashion Boutique',
    task: 'Posted to Instagram and TikTok',
    time: '4 hours ago',
    status: 'completed',
  },
  {
    id: 3,
    instance: 'Lifestyle Blog',
    task: 'Analyzing competitor content strategy',
    time: '5 hours ago',
    status: 'in_progress',
  },
]

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back! Here&apos;s an overview of your business operations.
          </p>
        </div>
        <Link href="/instances/new">
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            New Instance
          </Button>
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
              <stat.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">{stat.description}</p>
              <p className="mt-2 text-xs text-green-600">{stat.trend}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Latest tasks across all your instances</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentActivity.map((activity) => (
              <div
                key={activity.id}
                className="flex items-center justify-between rounded-lg border p-4"
              >
                <div className="space-y-1">
                  <p className="text-sm font-medium">{activity.instance}</p>
                  <p className="text-sm text-muted-foreground">{activity.task}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-muted-foreground">{activity.time}</p>
                  <p
                    className={cn(
                      'text-xs font-medium',
                      activity.status === 'completed'
                        ? 'text-green-600'
                        : 'text-yellow-600'
                    )}
                  >
                    {activity.status === 'completed' ? 'Completed' : 'In Progress'}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="cursor-pointer transition-colors hover:bg-secondary/50">
          <CardHeader>
            <CardTitle className="text-lg">Submit a Task</CardTitle>
            <CardDescription>
              Tell your AI agents what you need done
            </CardDescription>
          </CardHeader>
        </Card>
        <Card className="cursor-pointer transition-colors hover:bg-secondary/50">
          <CardHeader>
            <CardTitle className="text-lg">View Analytics</CardTitle>
            <CardDescription>
              Check performance across all instances
            </CardDescription>
          </CardHeader>
        </Card>
        <Card className="cursor-pointer transition-colors hover:bg-secondary/50">
          <CardHeader>
            <CardTitle className="text-lg">Manage Agents</CardTitle>
            <CardDescription>
              Configure your AI team&apos;s capabilities
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    </div>
  )
}

