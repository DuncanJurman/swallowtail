'use client'

import { useState } from 'react'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import { AlertCircle, Video, User, Lock, Globe, Users } from 'lucide-react'
import { usePostToTikTok, useTikTokAccounts } from '@/lib/hooks/use-tiktok-post'
import { useToast } from '@/components/ui/use-toast'

interface TikTokPostDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  taskData: {
    id: string
    description: string
    output_data: {
      video_url: string
      thumbnail_url: string
      suggested_caption: string
      duration_seconds: number
      resolution: string
    }
  }
  instanceId: string
}

export default function TikTokPostDialog({ 
  open, 
  onOpenChange, 
  taskData,
  instanceId 
}: TikTokPostDialogProps) {
  const [caption, setCaption] = useState(taskData.output_data.suggested_caption)
  const [privacyLevel, setPrivacyLevel] = useState('SELF_ONLY')
  const [disableDuet, setDisableDuet] = useState(false)
  const [disableStitch, setDisableStitch] = useState(false)
  const [disableComment, setDisableComment] = useState(false)
  const [selectedAccount, setSelectedAccount] = useState('')
  
  const { toast } = useToast()
  const postToTikTok = usePostToTikTok()
  const { data: accountsData } = useTikTokAccounts(instanceId)

  // Use real accounts if available, otherwise use mock data
  const accounts = accountsData?.accounts || [
    { id: '1', name: 'Main Account', username: '@testuser', isDefault: true },
    { id: '2', name: 'Product Showcase', username: '@products', isDefault: false }
  ]

  const handlePost = async () => {
    const postData = {
      taskId: taskData.id,
      title: caption,
      privacy_level: privacyLevel,
      disable_duet: disableDuet,
      disable_stitch: disableStitch,
      disable_comment: disableComment,
      account_id: selectedAccount || accounts[0]?.id
    }

    postToTikTok.mutate(postData, {
      onSuccess: () => {
        toast({
          title: 'Success',
          description: 'Video has been queued for posting to TikTok',
          variant: 'default'
        })
        onOpenChange(false)
      },
      onError: (error) => {
        const err = error as { response?: { data?: { detail?: string } } }
        toast({
          title: 'Error',
          description: err.response?.data?.detail || 'Failed to post to TikTok',
          variant: 'destructive'
        })
      }
    })
  }

  const getPrivacyIcon = () => {
    switch (privacyLevel) {
      case 'PUBLIC_TO_EVERYONE':
        return <Globe className="h-4 w-4" />
      case 'MUTUAL_FOLLOW_FRIENDS':
        return <Users className="h-4 w-4" />
      case 'SELF_ONLY':
        return <Lock className="h-4 w-4" />
      default:
        return <Lock className="h-4 w-4" />
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Post Video to TikTok</DialogTitle>
          <DialogDescription>
            Review and customize your video post before sharing
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-6 py-4">
          {/* Sandbox Mode Warning */}
          <div className="flex items-start gap-2 p-3 bg-amber-50 dark:bg-amber-950/20 rounded-lg border border-amber-200 dark:border-amber-800">
            <AlertCircle className="h-5 w-5 text-amber-600 dark:text-amber-500 mt-0.5" />
            <div className="space-y-1">
              <p className="text-sm font-medium text-amber-900 dark:text-amber-100">
                Sandbox Mode Active
              </p>
              <p className="text-sm text-amber-700 dark:text-amber-300">
                Posts will only be visible to you. Switch to production mode for public posting.
              </p>
            </div>
          </div>

          {/* Video Preview */}
          <div className="space-y-2">
            <Label>Video Preview</Label>
            <Card className="p-4">
              <div className="grid grid-cols-[auto,1fr] gap-4">
                <div className="w-32 aspect-[9/16] bg-secondary rounded-lg overflow-hidden">
                  <video
                    src={taskData.output_data.video_url}
                    poster={taskData.output_data.thumbnail_url}
                    className="w-full h-full object-cover"
                    muted
                  />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Video className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Video Details</span>
                  </div>
                  <div className="text-sm text-muted-foreground space-y-1">
                    <p>Duration: {taskData.output_data.duration_seconds} seconds</p>
                    <p>Resolution: {taskData.output_data.resolution}</p>
                    <p>Format: MP4</p>
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* Caption */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <Label htmlFor="caption">Caption</Label>
              <span className="text-sm text-muted-foreground">
                {caption.length}/2200
              </span>
            </div>
            <Textarea
              id="caption"
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              placeholder="Write a caption..."
              className="min-h-[100px]"
              maxLength={2200}
            />
          </div>

          {/* Account Selector */}
          <div className="space-y-2">
            <Label htmlFor="account">TikTok Account</Label>
            <Select value={selectedAccount} onValueChange={setSelectedAccount}>
              <SelectTrigger id="account">
                <SelectValue placeholder="Select an account">
                  {selectedAccount && (
                    <div className="flex items-center gap-2">
                      <User className="h-4 w-4" />
                      {accounts.find(a => a.id === selectedAccount)?.name}
                    </div>
                  )}
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                {accounts.map((account) => (
                  <SelectItem key={account.id} value={account.id}>
                    <div className="flex items-center justify-between w-full">
                      <div className="flex items-center gap-2">
                        <User className="h-4 w-4" />
                        <span>{account.name}</span>
                      </div>
                      <span className="text-muted-foreground text-sm ml-4">
                        {account.username}
                      </span>
                      {account.isDefault && (
                        <Badge variant="secondary" className="ml-2">
                          Default
                        </Badge>
                      )}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Privacy Settings */}
          <div className="space-y-2">
            <Label htmlFor="privacy">Privacy Level</Label>
            <Select value={privacyLevel} onValueChange={setPrivacyLevel}>
              <SelectTrigger id="privacy">
                <SelectValue>
                  <div className="flex items-center gap-2">
                    {getPrivacyIcon()}
                    <span>
                      {privacyLevel === 'PUBLIC_TO_EVERYONE' && 'Everyone'}
                      {privacyLevel === 'MUTUAL_FOLLOW_FRIENDS' && 'Friends'}
                      {privacyLevel === 'SELF_ONLY' && 'Only Me'}
                    </span>
                  </div>
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="SELF_ONLY">
                  <div className="flex items-center gap-2">
                    <Lock className="h-4 w-4" />
                    <span>Only Me (Sandbox Default)</span>
                  </div>
                </SelectItem>
                <SelectItem value="MUTUAL_FOLLOW_FRIENDS" disabled>
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4" />
                    <span>Friends (Production Only)</span>
                  </div>
                </SelectItem>
                <SelectItem value="PUBLIC_TO_EVERYONE" disabled>
                  <div className="flex items-center gap-2">
                    <Globe className="h-4 w-4" />
                    <span>Everyone (Production Only)</span>
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Interaction Settings */}
          <div className="space-y-3">
            <Label>Interaction Settings</Label>
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="disable-duet"
                  checked={disableDuet}
                  onCheckedChange={(checked) => setDisableDuet(checked as boolean)}
                />
                <label
                  htmlFor="disable-duet"
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  Disable Duet
                </label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="disable-stitch"
                  checked={disableStitch}
                  onCheckedChange={(checked) => setDisableStitch(checked as boolean)}
                />
                <label
                  htmlFor="disable-stitch"
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  Disable Stitch
                </label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="disable-comment"
                  checked={disableComment}
                  onCheckedChange={(checked) => setDisableComment(checked as boolean)}
                />
                <label
                  htmlFor="disable-comment"
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  Disable Comments
                </label>
              </div>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={postToTikTok.isPending}
          >
            Cancel
          </Button>
          <Button
            onClick={handlePost}
            disabled={postToTikTok.isPending || !caption.trim()}
          >
            {postToTikTok.isPending ? 'Posting...' : 'Post Now'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}