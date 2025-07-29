'use client'

import { useState } from 'react'
import { Button } from '../ui/button'
import { Textarea } from '../ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { 
  Send, 
  Calendar, 
  AlertCircle, 
  Sparkles,
  Clock,
  ChevronDown,
  ChevronUp
} from 'lucide-react'
import { TaskPriority } from '../../types/task'
import { cn } from '../../lib/utils'

interface TaskInputProps {
  instanceId: string
  onSubmit: (task: {
    description: string
    priority: TaskPriority
    scheduled_for?: string
  }) => void
  isLoading?: boolean
}

export function TaskInput({ onSubmit, isLoading = false }: TaskInputProps) {
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState<TaskPriority>(TaskPriority.NORMAL)
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [scheduledFor, setScheduledFor] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!description.trim()) return

    onSubmit({
      description: description.trim(),
      priority,
      scheduled_for: scheduledFor || undefined,
    })

    // Reset form
    setDescription('')
    setPriority(TaskPriority.NORMAL)
    setScheduledFor('')
    setShowAdvanced(false)
  }

  const priorityOptions = [
    { value: TaskPriority.URGENT, label: 'Urgent', color: 'text-red-600' },
    { value: TaskPriority.NORMAL, label: 'Normal', color: 'text-blue-600' },
    { value: TaskPriority.LOW, label: 'Low', color: 'text-gray-600' },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-[--color-primary]" />
          Submit a Task
        </CardTitle>
        <CardDescription>
          Describe what you need done in natural language. Your AI agents will understand and execute.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Task Description */}
          <div className="space-y-2">
            <Textarea
              placeholder="e.g., Create 5 Instagram posts about our new product launch, focusing on sustainability features..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="min-h-[120px] resize-none"
              disabled={isLoading}
            />
            <p className="text-xs text-[--color-muted-foreground]">
              Be specific about what you want. The more detail you provide, the better the results.
            </p>
          </div>

          {/* Priority Selection */}
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">Priority:</span>
            <div className="flex gap-2">
              {priorityOptions.map((option) => (
                <Button
                  key={option.value}
                  type="button"
                  variant={priority === option.value ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setPriority(option.value)}
                  disabled={isLoading}
                  className={cn(
                    priority === option.value && option.value === TaskPriority.URGENT && 'bg-red-600 hover:bg-red-700',
                    priority === option.value && option.value === TaskPriority.LOW && 'bg-gray-600 hover:bg-gray-700'
                  )}
                >
                  <AlertCircle className={cn('mr-1 h-3 w-3', option.color)} />
                  {option.label}
                </Button>
              ))}
            </div>
          </div>

          {/* Advanced Options Toggle */}
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="w-full justify-between"
          >
            Advanced Options
            {showAdvanced ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </Button>

          {/* Advanced Options */}
          {showAdvanced && (
            <div className="space-y-3 rounded-lg border p-4">
              <div className="space-y-2">
                <label htmlFor="schedule" className="flex items-center gap-2 text-sm font-medium">
                  <Calendar className="h-4 w-4" />
                  Schedule for later
                </label>
                <input
                  type="datetime-local"
                  id="schedule"
                  value={scheduledFor}
                  onChange={(e) => setScheduledFor(e.target.value)}
                  className="flex h-10 w-full rounded-md border border-[--color-input] bg-[--color-background] px-3 py-2 text-sm"
                  disabled={isLoading}
                />
              </div>
            </div>
          )}

          {/* Submit Button */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-[--color-muted-foreground]">
              <Clock className="h-4 w-4" />
              <span>Tasks typically complete in 2-5 minutes</span>
            </div>
            <Button
              type="submit"
              disabled={!description.trim() || isLoading}
              className="gap-2"
            >
              <Send className="h-4 w-4" />
              {isLoading ? 'Submitting...' : 'Submit Task'}
            </Button>
          </div>
        </form>

        {/* Example Tasks */}
        <div className="mt-6 space-y-2">
          <p className="text-sm font-medium text-[--color-muted-foreground]">Example tasks:</p>
          <div className="flex flex-wrap gap-2">
            {[
              'Research competitor pricing',
              'Generate product descriptions',
              'Create social media content',
              'Analyze customer feedback',
            ].map((example) => (
              <Badge
                key={example}
                variant="outline"
                className="cursor-pointer"
                onClick={() => setDescription(example)}
              >
                {example}
              </Badge>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}