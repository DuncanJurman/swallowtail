'use client'

import { useWebSocket } from '@/providers/websocket-provider'
import { Badge } from '@/components/ui/badge'
import { Wifi, WifiOff } from 'lucide-react'

export function Header() {
  const { connected } = useWebSocket()

  return (
    <header className="flex h-16 items-center justify-between border-b bg-white px-6">
      <h2 className="text-lg font-semibold">E-Commerce Automation Dashboard</h2>
      
      <div className="flex items-center gap-4">
        <Badge variant={connected ? 'default' : 'destructive'} className="flex items-center gap-1">
          {connected ? (
            <>
              <Wifi className="h-3 w-3" />
              Connected
            </>
          ) : (
            <>
              <WifiOff className="h-3 w-3" />
              Disconnected
            </>
          )}
        </Badge>
      </div>
    </header>
  )
}