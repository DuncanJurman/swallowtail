'use client'

import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { useToast } from '@/hooks/use-toast'
import { checkpointsApi } from '@/services/api'
import type { HumanCheckpoint, CheckpointType, ProductIdea } from '@/types'
import { ProductSelectionView } from './product-selection-view'
import { CheckCircle, XCircle } from 'lucide-react'

interface CheckpointCardProps {
  checkpoint: HumanCheckpoint
}

export function CheckpointCard({ checkpoint }: CheckpointCardProps) {
  const [notes, setNotes] = useState('')
  const [selectedProduct, setSelectedProduct] = useState<ProductIdea | null>(null)
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const resolveMutation = useMutation({
    mutationFn: (approved: boolean) => {
      const resolution = {
        approved,
        notes: notes || undefined,
        data: selectedProduct ? { selected_product: selectedProduct } : undefined,
      }
      return checkpointsApi.resolve(checkpoint.id, resolution)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['checkpoints'] })
      queryClient.invalidateQueries({ queryKey: ['workflow-status'] })
      toast({
        title: 'Checkpoint Resolved',
        description: 'The checkpoint has been processed successfully',
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to resolve checkpoint',
        variant: 'destructive',
      })
    },
  })

  const handleApprove = () => {
    if (checkpoint.type === 'product_selection' && !selectedProduct) {
      toast({
        title: 'Product Required',
        description: 'Please select a product before approving',
        variant: 'destructive',
      })
      return
    }
    resolveMutation.mutate(true)
  }

  const handleReject = () => {
    resolveMutation.mutate(false)
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle>{checkpoint.title}</CardTitle>
            <CardDescription>{checkpoint.description}</CardDescription>
          </div>
          <Badge variant="outline">{checkpoint.type.replace(/_/g, ' ')}</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {checkpoint.type === 'product_selection' && (
          <ProductSelectionView 
            products={checkpoint.data.products || []}
            onSelectProduct={setSelectedProduct}
            selectedProduct={selectedProduct}
          />
        )}
        
        <div className="space-y-2">
          <label htmlFor={`notes-${checkpoint.id}`} className="text-sm font-medium">
            Notes (optional)
          </label>
          <Textarea
            id={`notes-${checkpoint.id}`}
            placeholder="Add any notes or feedback..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
          />
        </div>
        
        <div className="flex gap-2">
          <Button
            onClick={handleApprove}
            disabled={resolveMutation.isPending}
            className="flex-1"
          >
            <CheckCircle className="mr-2 h-4 w-4" />
            Approve
          </Button>
          <Button
            onClick={handleReject}
            disabled={resolveMutation.isPending}
            variant="destructive"
            className="flex-1"
          >
            <XCircle className="mr-2 h-4 w-4" />
            Reject
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}