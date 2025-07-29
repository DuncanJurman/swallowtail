// Tailwind v4 color utility mapping
// Maps old variable-based colors to new Tailwind v4 color system

export const colorMap = {
  // Background colors
  'bg-background': 'bg-[--color-background]',
  'bg-foreground': 'bg-[--color-foreground]',
  'bg-card': 'bg-[--color-card]',
  'bg-popover': 'bg-[--color-popover]',
  'bg-primary': 'bg-[--color-primary]',
  'bg-primary-foreground': 'bg-[--color-primary-foreground]',
  'bg-secondary': 'bg-[--color-secondary]',
  'bg-secondary-foreground': 'bg-[--color-secondary-foreground]',
  'bg-muted': 'bg-[--color-muted]',
  'bg-muted-foreground': 'bg-[--color-muted-foreground]',
  'bg-accent': 'bg-[--color-accent]',
  'bg-accent-foreground': 'bg-[--color-accent-foreground]',
  'bg-destructive': 'bg-[--color-destructive]',
  'bg-destructive-foreground': 'bg-[--color-destructive-foreground]',
  'bg-input': 'bg-[--color-input]',
  
  // Text colors
  'text-background': 'text-[--color-background]',
  'text-foreground': 'text-[--color-foreground]',
  'text-card': 'text-[--color-card]',
  'text-card-foreground': 'text-[--color-card-foreground]',
  'text-popover': 'text-[--color-popover]',
  'text-popover-foreground': 'text-[--color-popover-foreground]',
  'text-primary': 'text-[--color-primary]',
  'text-primary-foreground': 'text-[--color-primary-foreground]',
  'text-secondary': 'text-[--color-secondary]',
  'text-secondary-foreground': 'text-[--color-secondary-foreground]',
  'text-muted': 'text-[--color-muted]',
  'text-muted-foreground': 'text-[--color-muted-foreground]',
  'text-accent': 'text-[--color-accent]',
  'text-accent-foreground': 'text-[--color-accent-foreground]',
  'text-destructive': 'text-[--color-destructive]',
  'text-destructive-foreground': 'text-[--color-destructive-foreground]',
  
  // Border colors
  'border-background': 'border-[--color-background]',
  'border-foreground': 'border-[--color-foreground]',
  'border-border': 'border-[--color-border]',
  'border-input': 'border-[--color-input]',
  'border-primary': 'border-[--color-primary]',
  'border-secondary': 'border-[--color-secondary]',
  'border-muted': 'border-[--color-muted]',
  'border-accent': 'border-[--color-accent]',
  'border-destructive': 'border-[--color-destructive]',
  
  // Ring colors
  'ring-ring': 'ring-[--color-ring]',
  'ring-primary': 'ring-[--color-primary]',
  'ring-offset-background': 'ring-offset-[--color-background]',
  
  // Focus colors
  'focus:ring-ring': 'focus:ring-[--color-ring]',
  'focus:ring-primary': 'focus:ring-[--color-primary]',
  'focus:border-input': 'focus:border-[--color-input]',
  
  // Hover colors
  'hover:bg-primary': 'hover:bg-[--color-primary]',
  'hover:bg-secondary': 'hover:bg-[--color-secondary]',
  'hover:bg-muted': 'hover:bg-[--color-muted]',
  'hover:bg-accent': 'hover:bg-[--color-accent]',
  'hover:bg-destructive': 'hover:bg-[--color-destructive]',
  'hover:text-accent-foreground': 'hover:text-[--color-accent-foreground]',
  
  // Additional semantic colors
  'bg-success-500': 'bg-[--color-success-500]',
  'bg-warning-500': 'bg-[--color-warning-500]',
  'bg-error-500': 'bg-[--color-error-500]',
  'text-success-700': 'text-[--color-success-700]',
  'text-warning-700': 'text-[--color-warning-700]',
  'text-error-700': 'text-[--color-error-700]',
  'text-gray-500': 'text-[--color-gray-500]',
  'text-gray-600': 'text-[--color-gray-600]',
  'text-gray-700': 'text-[--color-gray-700]',
  'bg-gray-50': 'bg-[--color-gray-50]',
  'bg-gray-100': 'bg-[--color-gray-100]',
  'border-gray-200': 'border-[--color-gray-200]',
  'border-gray-300': 'border-[--color-gray-300]',
} as const

// Helper function to replace color classes in a string
export function replaceColorClasses(classString: string): string {
  let result = classString
  Object.entries(colorMap).forEach(([oldClass, newClass]) => {
    const regex = new RegExp(`\\b${oldClass}\\b`, 'g')
    result = result.replace(regex, newClass)
  })
  return result
}