'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../../../components/ui/card'
import { Button } from '../../../../../components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../../../components/ui/tabs'
import { TikTokConnection } from '../../../../../components/instances/settings/tiktok-connection'
import { Settings, Bell, Shield, Zap } from 'lucide-react'

interface SettingsPageClientProps {
  instanceId: string
}

export default function SettingsPageClient({ instanceId }: SettingsPageClientProps) {
  const [activeTab, setActiveTab] = useState('general')

  return (
    <div className="container mx-auto max-w-6xl p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Instance Settings</h1>
        <p className="text-muted-foreground mt-2">
          Manage your instance configuration and platform connections
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4 lg:w-[600px]">
          <TabsTrigger value="general" className="flex items-center gap-2">
            <Settings className="h-4 w-4" />
            General
          </TabsTrigger>
          <TabsTrigger value="platforms" className="flex items-center gap-2">
            <Zap className="h-4 w-4" />
            Platforms
          </TabsTrigger>
          <TabsTrigger value="notifications" className="flex items-center gap-2">
            <Bell className="h-4 w-4" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="advanced" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Advanced
          </TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>General Settings</CardTitle>
              <CardDescription>
                Configure basic instance settings and preferences
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Instance Name</label>
                <input
                  type="text"
                  className="w-full rounded-md border px-3 py-2"
                  placeholder="My Ecommerce Store"
                  disabled
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Description</label>
                <textarea
                  className="w-full rounded-md border px-3 py-2"
                  rows={3}
                  placeholder="A brief description of your instance..."
                  disabled
                />
              </div>
              <Button disabled>Save Changes</Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="platforms" className="space-y-6">
          <div className="space-y-6">
            {/* TikTok Connection Section */}
            <TikTokConnection instanceId={instanceId} />

            {/* Other Platform Connections (placeholder) */}
            <Card>
              <CardHeader>
                <CardTitle>Other Platforms</CardTitle>
                <CardDescription>
                  Connect additional platforms to expand your reach
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2">
                  {['Instagram', 'YouTube', 'Facebook', 'Twitter'].map((platform) => (
                    <div
                      key={platform}
                      className="flex items-center justify-between rounded-lg border p-4"
                    >
                      <div>
                        <h4 className="font-medium">{platform}</h4>
                        <p className="text-sm text-muted-foreground">Not connected</p>
                      </div>
                      <Button variant="outline" size="sm" disabled>
                        Coming Soon
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Notification Preferences</CardTitle>
              <CardDescription>
                Configure how you receive updates about your instance
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">Notification settings coming soon...</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="advanced" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Advanced Settings</CardTitle>
              <CardDescription>
                Advanced configuration options for power users
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">Advanced settings coming soon...</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}