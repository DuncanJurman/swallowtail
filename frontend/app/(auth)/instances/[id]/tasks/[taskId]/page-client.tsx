'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { 
  ChevronLeft, 
  ClipboardList, 
  MessageSquare, 
  Video
} from 'lucide-react'
import { useRouter } from 'next/navigation'
import TikTokPostDialog from '@/components/tasks/tiktok-post-dialog'
import { useTaskDetail } from '@/lib/hooks/use-tiktok-post'

interface TaskDetailClientProps {
  instanceId: string
  taskId: string
}

export default function TaskDetailClient({ instanceId, taskId }: TaskDetailClientProps) {
  const router = useRouter()
  const [showTikTokDialog, setShowTikTokDialog] = useState(false)
  const [postToTikTok, setPostToTikTok] = useState(false)
  
  // Fetch task details
  const { data: taskData, isLoading } = useTaskDetail(taskId)
  
  if (isLoading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 bg-secondary rounded w-1/3"></div>
        <div className="grid gap-6">
          <div className="h-64 bg-secondary rounded"></div>
          <div className="h-64 bg-secondary rounded"></div>
          <div className="h-64 bg-secondary rounded"></div>
        </div>
      </div>
    )
  }

  // Test data for demo tasks
  const getTestTaskData = (id: string) => {
    interface TestTask {
      id: string
      description: string
      status: string
      priority: string
      output_data: {
        video_url: string
        thumbnail_url: string
        suggested_caption: string
        media_type: string
        duration_seconds: number
        resolution: string
      }
      tiktok_post_status: string | null
      created_at: string
      updated_at: string
    }
    const testTasks: Record<string, TestTask> = {
      'test-task-1': {
        id: 'test-task-1',
        description: 'Create an engaging TikTok video showcasing our new RGB LED gaming mouse with 7 programmable buttons',
        status: 'completed',
        priority: 'normal',
        output_data: {
          video_url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
          thumbnail_url: 'https://images.unsplash.com/photo-1527814050087-3793815479db?w=800',
          suggested_caption: '🎮 Level up your gaming with our new RGB LED mouse! ✨ 7 programmable buttons for ultimate control 🔥 #GamingMouse #RGBLighting #TechGadgets #GamerLife #PCGaming',
          media_type: 'video',
          duration_seconds: 60,
          resolution: '1080x1920'
        },
        tiktok_post_status: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      'test-task-2': {
        id: 'test-task-2',
        description: 'Create a trendy video showing our new summer dress collection with transitions',
        status: 'completed',
        priority: 'urgent',
        output_data: {
          video_url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
          thumbnail_url: 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800',
          suggested_caption: '☀️ Summer vibes only! Check out our new collection 👗 Use code SUMMER20 for 20% off! 🛍️ #SummerFashion #OOTD #FashionTrends #StyleInspo #NewCollection',
          media_type: 'video',
          duration_seconds: 45,
          resolution: '1080x1920'
        },
        tiktok_post_status: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      'test-task-3': {
        id: 'test-task-3',
        description: 'Create an inspiring video about productive morning routines',
        status: 'completed',
        priority: 'normal',
        output_data: {
          video_url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4',
          thumbnail_url: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800',
          suggested_caption: '🌅 Start your day right! My 5-minute morning routine for productivity 💪 #MorningRoutine #Productivity #HealthyLifestyle #Motivation #SelfCare',
          media_type: 'video',
          duration_seconds: 90,
          resolution: '1080x1920'
        },
        tiktok_post_status: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    }
    
    return testTasks[id] || null
  }

  // Use real data if available, otherwise check for test data, otherwise use default mock
  const mockTask = taskData?.task || getTestTaskData(taskId) || {
    id: taskId,
    description: 'Create TikTok video showcasing new LED product',
    status: 'completed',
    priority: 'normal',
    output_data: {
      video_url: 'https://example.com/video.mp4',
      thumbnail_url: 'https://example.com/thumb.jpg',
      suggested_caption: '✨ Transform your space with our new LED smart lights! 🌈 #SmartHome #LEDLights #HomeDecor',
      media_type: 'video',
      duration_seconds: 30,
      resolution: '1080x1920'
    },
    tiktok_post_status: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }

  const mockPlanningSteps = taskData?.planning?.steps || [
    { id: 1, description: 'Analyze task requirements', status: 'completed' },
    { id: 2, description: 'Generate video script', status: 'completed' },
    { id: 3, description: 'Create video content', status: 'completed' },
    { id: 4, description: 'Review and optimize', status: 'completed' }
  ]

  const mockExecutionLogs = taskData?.execution_logs || [
    {
      timestamp: new Date().toISOString(),
      agent: 'Manager Agent',
      action: 'Task analysis started',
      level: 'info',
      details: 'Analyzing requirements for TikTok video creation'
    },
    {
      timestamp: new Date().toISOString(),
      agent: 'Content Creator',
      action: 'Script generation',
      level: 'info',
      details: 'Generated video script with 5 scenes'
    }
  ]

  const mockAttachedMedia = taskData?.attached_media || [
    {
      id: '1',
      url: 'https://via.placeholder.com/200',
      type: 'reference',
      caption: 'Product reference image'
    }
  ]

  const handlePostToTikTok = () => {
    if (postToTikTok) {
      setShowTikTokDialog(true)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button 
            variant="ghost" 
            size="icon"
            onClick={() => router.push(`/instances/${instanceId}/tasks`)}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold">Task Details</h1>
            <p className="text-muted-foreground">{mockTask.description}</p>
          </div>
        </div>
        <Badge variant={mockTask.status === 'completed' ? 'default' : 'secondary'}>
          {mockTask.status}
        </Badge>
      </div>

      {/* Three-Section Layout with Tabs */}
      <Tabs defaultValue="planning" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="planning" className="flex items-center gap-2">
            <ClipboardList className="h-4 w-4" />
            Planning
          </TabsTrigger>
          <TabsTrigger value="logs" className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4" />
            Agent Logs
          </TabsTrigger>
          <TabsTrigger value="output" className="flex items-center gap-2">
            <Video className="h-4 w-4" />
            Output
          </TabsTrigger>
        </TabsList>

        {/* Section 1: Task Planning */}
        <TabsContent value="planning" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Task Planning</CardTitle>
              <CardDescription>
                Execution plan created by the Manager Agent
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Planning Steps */}
              <div className="space-y-2">
                {mockPlanningSteps.map((step) => (
                  <div key={step.id} className="flex items-center gap-3 p-2 rounded-lg border">
                    <Checkbox checked={step.status === 'completed'} disabled />
                    <span className={step.status === 'completed' ? 'line-through text-muted-foreground' : ''}>
                      {step.description}
                    </span>
                  </div>
                ))}
              </div>

              {/* Attached Media */}
              {mockAttachedMedia.length > 0 && (
                <div className="pt-4 border-t">
                  <h4 className="text-sm font-semibold mb-2">Reference Images</h4>
                  <div className="grid grid-cols-3 gap-2">
                    {mockAttachedMedia.map((media) => (
                      <div key={media.id} className="relative aspect-square rounded-lg overflow-hidden border">
                        <img 
                          src={media.url} 
                          alt={media.caption}
                          className="object-cover w-full h-full"
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Section 2: Agent Execution Logs */}
        <TabsContent value="logs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Agent Execution Logs</CardTitle>
              <CardDescription>
                Real-time activity from task agents (coming soon)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {mockExecutionLogs.map((log, index) => (
                  <div key={index} className="p-3 rounded-lg border space-y-1">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs">
                          {log.agent}
                        </Badge>
                        <span className="text-sm font-medium">{log.action}</span>
                      </div>
                      <span className="text-xs text-muted-foreground">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground">{log.details}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Section 3: Final Output */}
        <TabsContent value="output" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Task Output</CardTitle>
              <CardDescription>
                Generated content and results
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {mockTask.output_data?.media_type === 'video' && mockTask.output_data && (
                <>
                  {/* Video Preview */}
                  <div className="aspect-video bg-secondary rounded-lg overflow-hidden">
                    <video
                      src={mockTask.output_data.video_url}
                      poster={mockTask.output_data.thumbnail_url}
                      controls
                      className="w-full h-full object-contain"
                    >
                      Your browser does not support the video tag.
                    </video>
                  </div>

                  {/* Video Details */}
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Duration:</span>{' '}
                      <span className="font-medium">{mockTask.output_data.duration_seconds}s</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Resolution:</span>{' '}
                      <span className="font-medium">{mockTask.output_data.resolution}</span>
                    </div>
                  </div>

                  {/* Suggested Caption */}
                  <div className="space-y-2">
                    <h4 className="text-sm font-semibold">Suggested Caption</h4>
                    <p className="text-sm p-3 bg-secondary rounded-lg">
                      {mockTask.output_data.suggested_caption}
                    </p>
                  </div>

                  {/* Post to TikTok Option */}
                  {mockTask.status === 'completed' && !mockTask.tiktok_post_status && (
                    <div className="pt-4 border-t">
                      <div className="flex items-center space-x-2">
                        <Checkbox 
                          id="post-to-tiktok"
                          checked={postToTikTok}
                          onCheckedChange={(checked) => {
                            setPostToTikTok(checked as boolean)
                            if (checked) {
                              handlePostToTikTok()
                            }
                          }}
                        />
                        <label
                          htmlFor="post-to-tiktok"
                          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                        >
                          Post to TikTok
                        </label>
                      </div>
                      {postToTikTok && (
                        <p className="text-xs text-muted-foreground mt-2 ml-6">
                          Click to open posting options (Sandbox Mode - posts will be private)
                        </p>
                      )}
                    </div>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* TikTok Posting Dialog */}
      {mockTask.output_data && (
        <TikTokPostDialog
          open={showTikTokDialog}
          onOpenChange={setShowTikTokDialog}
          taskData={{
            id: mockTask.id,
            description: mockTask.description,
            output_data: mockTask.output_data
          }}
          instanceId={instanceId}
        />
      )}
    </div>
  )
}