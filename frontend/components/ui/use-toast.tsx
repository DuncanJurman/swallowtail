import * as React from 'react'

export interface Toast {
  id: string
  title?: string
  description?: string
  action?: React.ReactNode
  variant?: 'default' | 'destructive'
}

interface ToastContextType {
  toasts: Toast[]
  toast: (props: Omit<Toast, 'id'>) => void
  dismiss: (toastId?: string) => void
}

const ToastContext = React.createContext<ToastContextType | undefined>(undefined)

export function useToast() {
  const context = React.useContext(ToastContext)
  if (!context) {
    // Return a mock implementation if not in provider
    return {
      toast: (props: Omit<Toast, 'id'>) => {
        console.log('Toast:', props)
      },
      dismiss: () => {},
      toasts: []
    }
  }
  return context
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = React.useState<Toast[]>([])

  const toast = React.useCallback((props: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9)
    const newToast = { ...props, id }
    setToasts((prev) => [...prev, newToast])
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, 5000)
  }, [])

  const dismiss = React.useCallback((toastId?: string) => {
    if (toastId) {
      setToasts((prev) => prev.filter((t) => t.id !== toastId))
    } else {
      setToasts([])
    }
  }, [])

  return (
    <ToastContext.Provider value={{ toasts, toast, dismiss }}>
      {children}
    </ToastContext.Provider>
  )
}