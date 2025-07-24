import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'

import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-[--color-ring] focus:ring-offset-2',
  {
    variants: {
      variant: {
        default:
          'border-transparent bg-[--color-primary] text-[--color-primary-foreground] hover:bg-[--color-primary]/80',
        secondary:
          'border-transparent bg-[--color-secondary] text-[--color-secondary-foreground] hover:bg-[--color-secondary]/80',
        destructive:
          'border-transparent bg-[--color-destructive] text-[--color-destructive-foreground] hover:bg-[--color-destructive]/80',
        outline: 'text-[--color-foreground]',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }