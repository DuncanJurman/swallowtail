import { Button } from '@/components/ui/button'
import { InstanceCard } from '@/components/instances/instance-card'
import { Instance, InstanceType } from '@/types/instance'
import { Plus, Filter } from 'lucide-react'
import Link from 'next/link'

// Mock data - will be replaced with API calls
const mockInstances: Instance[] = [
  {
    id: 'ed047e11-67e0-40e7-8097-1251d4e7c6ab',
    name: 'Tech Gadgets Store',
    description: 'Electronics and gadgets ecommerce store',
    type: InstanceType.ECOMMERCE,
    business_profile: {
      mission: 'Provide cutting-edge technology products',
      target_audience: 'Tech enthusiasts',
      brand_voice: 'Professional and informative',
    },
    visual_identity: {
      primary_color: '#0EA5E9',
    },
    platform_connections: {
      instagram: { connected: true },
      tiktok: { connected: true },
      shopify: { connected: true },
    },
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-01-20T15:30:00Z',
    is_active: true,
  },
  {
    id: '6ba7b810-9dad-11d1-80b4-00c04fd430c8',
    name: 'Fashion Boutique',
    description: 'Trendy clothing and accessories',
    type: InstanceType.ECOMMERCE,
    business_profile: {
      mission: 'Empower individuals through fashion',
      target_audience: 'Young professionals',
      brand_voice: 'Trendy and inspiring',
    },
    visual_identity: {
      primary_color: '#D946EF',
    },
    platform_connections: {
      instagram: { connected: true },
      pinterest: { connected: true },
    },
    created_at: '2024-01-10T09:00:00Z',
    updated_at: '2024-01-19T14:20:00Z',
    is_active: true,
  },
  {
    id: '6ba7b814-9dad-11d1-80b4-00c04fd430c8',
    name: 'Lifestyle Blog',
    description: 'Health, wellness, and lifestyle content',
    type: InstanceType.SOCIAL_MEDIA,
    business_profile: {
      mission: 'Inspire healthy living',
      target_audience: 'Health-conscious millennials',
      brand_voice: 'Friendly and motivational',
    },
    visual_identity: {
      primary_color: '#22C55E',
    },
    platform_connections: {
      instagram: { connected: true },
      twitter: { connected: true },
      facebook: { connected: true },
    },
    created_at: '2024-01-05T11:00:00Z',
    updated_at: '2024-01-18T16:45:00Z',
    is_active: false,
  },
]

// Mock metrics
const mockMetrics: Record<string, { activeTasks: number; completedToday: number; activeAgents: number }> = {
  'ed047e11-67e0-40e7-8097-1251d4e7c6ab': { activeTasks: 3, completedToday: 12, activeAgents: 6 },
  '6ba7b810-9dad-11d1-80b4-00c04fd430c8': { activeTasks: 1, completedToday: 8, activeAgents: 5 },
  '6ba7b814-9dad-11d1-80b4-00c04fd430c8': { activeTasks: 0, completedToday: 0, activeAgents: 4 },
}

export default function InstancesPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Instances</h1>
          <p className="text-muted-foreground">
            Manage your business instances and their AI agents
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="gap-2">
            <Filter className="h-4 w-4" />
            Filter
          </Button>
          <Link href="/instances/new">
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              New Instance
            </Button>
          </Link>
        </div>
      </div>

      {/* Instance Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {mockInstances.map((instance) => (
          <InstanceCard
            key={instance.id}
            instance={instance}
            metrics={mockMetrics[instance.id]}
          />
        ))}
      </div>

      {/* Empty State */}
      {mockInstances.length === 0 && (
        <div className="flex flex-col items-center justify-center rounded-lg border border-dashed py-12">
          <div className="mx-auto flex max-w-[420px] flex-col items-center justify-center text-center">
            <div className="flex h-20 w-20 items-center justify-center rounded-full bg-muted">
              <Plus className="h-10 w-10 text-muted-foreground" />
            </div>
            <h3 className="mt-4 text-lg font-semibold">No instances created</h3>
            <p className="mb-4 mt-2 text-sm text-muted-foreground">
              Create your first instance to start managing your business with AI agents.
            </p>
            <Link href="/instances/new">
              <Button>Create Instance</Button>
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}