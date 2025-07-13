'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import type { ProductIdea } from '@/types'
import { CheckCircle, TrendingUp, Users, Target } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ProductSelectionViewProps {
  products: ProductIdea[]
  selectedProduct: ProductIdea | null
  onSelectProduct: (product: ProductIdea) => void
}

export function ProductSelectionView({ 
  products, 
  selectedProduct, 
  onSelectProduct 
}: ProductSelectionViewProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium">Select a product to proceed with:</h3>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {products.map((product, index) => (
          <Card 
            key={index}
            className={cn(
              "cursor-pointer transition-all hover:shadow-md",
              selectedProduct?.name === product.name && "ring-2 ring-primary"
            )}
            onClick={() => onSelectProduct(product)}
          >
            <CardHeader>
              <CardTitle className="flex items-start justify-between text-base">
                <span>{product.name}</span>
                {selectedProduct?.name === product.name && (
                  <CheckCircle className="h-5 w-5 text-primary" />
                )}
              </CardTitle>
              <p className="text-sm text-muted-foreground">{product.category}</p>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm">{product.description}</p>
              
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs">
                  <Users className="h-3 w-3" />
                  <span>{product.target_audience}</span>
                </div>
                
                {product.search_volume_trend && (
                  <div className="flex items-center gap-2 text-xs">
                    <TrendingUp className="h-3 w-3" />
                    <span>{product.search_volume_trend}</span>
                  </div>
                )}
                
                {product.competition_level && (
                  <div className="flex items-center gap-2 text-xs">
                    <Target className="h-3 w-3" />
                    <span>Competition: {product.competition_level}</span>
                  </div>
                )}
              </div>
              
              <div className="pt-2">
                <p className="text-xs font-medium mb-1">Key Benefits:</p>
                <div className="flex flex-wrap gap-1">
                  {product.key_benefits.slice(0, 3).map((benefit, i) => (
                    <Badge key={i} variant="secondary" className="text-xs">
                      {benefit}
                    </Badge>
                  ))}
                </div>
              </div>
              
              <div className="pt-2 border-t">
                <p className="text-xs text-muted-foreground">{product.rationale}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}