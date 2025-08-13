import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ArrowRight, Video, Image, FileText, Sparkles } from 'lucide-react'

// Test tasks with different states and content types
const testTasks = [
  {
    id: 'test-task-1',
    instanceId: 'ed047e11-67e0-40e7-8097-1251d4e7c6ab',
    instanceName: 'Tech Gadgets Store',
    title: 'LED Gaming Mouse Product Video',
    description: 'Create an engaging TikTok video showcasing our new RGB LED gaming mouse with 7 programmable buttons',
    status: 'completed',
    hasVideo: true,
    hasImages: true,
    videoUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
    thumbnailUrl: 'https://images.unsplash.com/photo-1527814050087-3793815479db?w=400',
    suggestedCaption: '🎮 Level up your gaming with our new RGB LED mouse! ✨ 7 programmable buttons for ultimate control 🔥 #GamingMouse #RGBLighting #TechGadgets #GamerLife #PCGaming',
  },
  {
    id: 'test-task-2', 
    instanceId: '6ba7b810-9dad-11d1-80b4-00c04fd430c8',
    instanceName: 'Fashion Boutique',
    title: 'Summer Collection Showcase',
    description: 'Create a trendy video showing our new summer dress collection with transitions',
    status: 'completed',
    hasVideo: true,
    hasImages: true,
    videoUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
    thumbnailUrl: 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=400',
    suggestedCaption: '☀️ Summer vibes only! Check out our new collection 👗 Use code SUMMER20 for 20% off! 🛍️ #SummerFashion #OOTD #FashionTrends #StyleInspo #NewCollection',
  },
  {
    id: 'test-task-3',
    instanceId: '6ba7b814-9dad-11d1-80b4-00c04fd430c8',
    instanceName: 'Lifestyle Blog',
    title: 'Morning Routine Tips',
    description: 'Create an inspiring video about productive morning routines',
    status: 'completed',
    hasVideo: true,
    hasImages: false,
    videoUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4',
    thumbnailUrl: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400',
    suggestedCaption: '🌅 Start your day right! My 5-minute morning routine for productivity 💪 #MorningRoutine #Productivity #HealthyLifestyle #Motivation #SelfCare',
  },
  {
    id: 'test-task-4',
    instanceId: 'ed047e11-67e0-40e7-8097-1251d4e7c6ab',
    instanceName: 'Tech Gadgets Store',
    title: 'Wireless Earbuds Unboxing',
    description: 'Create an unboxing video for our premium wireless earbuds',
    status: 'in_progress',
    hasVideo: false,
    hasImages: true,
    videoUrl: null,
    thumbnailUrl: 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400',
    suggestedCaption: '🎧 Unboxing our latest wireless earbuds! Premium sound quality at an affordable price 🎵 #TechUnboxing #WirelessEarbuds #TechReview',
  }
]

export default function TestTikTokPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-pink-500 to-purple-600 rounded-lg p-6 text-white">
        <div className="flex items-center gap-2 mb-2">
          <Sparkles className="h-5 w-5" />
          <Badge variant="secondary" className="bg-white/20 text-white border-white/30">
            Test Mode
          </Badge>
        </div>
        <h1 className="text-3xl font-bold mb-2">TikTok Posting Test Page</h1>
        <p className="text-white/90">
          Test the TikTok content posting feature with dummy tasks that have video outputs.
          Click on any completed task to see the full detail page with posting options.
        </p>
      </div>

      {/* Instructions */}
      <Card className="border-amber-200 bg-amber-50 dark:bg-amber-950/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            How to Test
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ol className="list-decimal list-inside space-y-2 text-sm">
            <li>Click on any <Badge variant="outline" className="ml-1">Completed</Badge> task below</li>
            <li>You&apos;ll see three tabs: Planning, Agent Logs, and Output</li>
            <li>Go to the Output tab to see the video and &quot;Post to TikTok&quot; checkbox</li>
            <li>Check the checkbox and click &quot;Post to TikTok&quot; button</li>
            <li>Review and customize the posting dialog with caption, privacy settings, etc.</li>
            <li>Click &quot;Post Now&quot; to simulate posting (sandbox mode)</li>
          </ol>
        </CardContent>
      </Card>

      {/* Test Tasks Grid */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Test Tasks with Video Content</h2>
        <div className="grid gap-4 md:grid-cols-2">
          {testTasks.map((task) => (
            <Card 
              key={task.id} 
              className={task.status === 'completed' ? 'hover:shadow-lg transition-shadow cursor-pointer' : 'opacity-75'}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <CardTitle className="text-lg">{task.title}</CardTitle>
                    <CardDescription>{task.instanceName}</CardDescription>
                  </div>
                  <Badge 
                    variant={task.status === 'completed' ? 'default' : 'secondary'}
                    className={task.status === 'completed' ? 'bg-green-500' : ''}
                  >
                    {task.status === 'completed' ? 'Completed' : 'In Progress'}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground mb-4">{task.description}</p>
                
                {/* Media indicators */}
                <div className="flex items-center gap-4 mb-4">
                  {task.hasVideo && (
                    <div className="flex items-center gap-1 text-sm">
                      <Video className="h-4 w-4 text-blue-500" />
                      <span>Video Ready</span>
                    </div>
                  )}
                  {task.hasImages && (
                    <div className="flex items-center gap-1 text-sm">
                      <Image className="h-4 w-4 text-green-500" />
                      <span>Images Attached</span>
                    </div>
                  )}
                </div>

                {/* Thumbnail preview */}
                {task.thumbnailUrl && (
                  <div className="relative aspect-video rounded-lg overflow-hidden mb-4 bg-secondary">
                    <img 
                      src={task.thumbnailUrl} 
                      alt={task.title}
                      className="w-full h-full object-cover"
                    />
                    {task.hasVideo && (
                      <div className="absolute inset-0 bg-black/30 flex items-center justify-center">
                        <div className="bg-white/90 rounded-full p-3">
                          <Video className="h-6 w-6 text-black" />
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Action button */}
                {task.status === 'completed' ? (
                  <Link href={`/instances/${task.instanceId}/tasks/${task.id}`}>
                    <Button className="w-full gap-2">
                      View Task Details
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </Link>
                ) : (
                  <Button className="w-full" disabled variant="secondary">
                    Task In Progress...
                  </Button>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Additional Info */}
      <Card>
        <CardHeader>
          <CardTitle>Test Data Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-muted-foreground">
          <p>
            <strong>Video URLs:</strong> Using sample videos from Google&apos;s test bucket (Big Buck Bunny, etc.)
          </p>
          <p>
            <strong>Instance IDs:</strong> Using the same IDs from the instances page for consistency
          </p>
          <p>
            <strong>Task IDs:</strong> test-task-1 through test-task-4 for easy identification
          </p>
          <p>
            <strong>Sandbox Mode:</strong> All posts will be private (SELF_ONLY) in TikTok sandbox mode
          </p>
        </CardContent>
      </Card>
    </div>
  )
}