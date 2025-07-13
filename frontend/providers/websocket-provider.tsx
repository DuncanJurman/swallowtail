'use client'

import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import io from 'socket.io-client'

type SocketType = ReturnType<typeof io>

interface WebSocketContextType {
  socket: SocketType | null
  connected: boolean
  subscribe: (event: string, handler: (data: any) => void) => void
  unsubscribe: (event: string, handler: (data: any) => void) => void
}

const WebSocketContext = createContext<WebSocketContextType>({
  socket: null,
  connected: false,
  subscribe: () => {},
  unsubscribe: () => {},
})

export const useWebSocket = () => useContext(WebSocketContext)

export function WebSocketProvider({ children }: { children: React.ReactNode }) {
  const [socket, setSocket] = useState<SocketType | null>(null)
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
    
    const socketInstance = io(WS_URL, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    })

    socketInstance.on('connect', () => {
      console.log('WebSocket connected')
      setConnected(true)
    })

    socketInstance.on('disconnect', () => {
      console.log('WebSocket disconnected')
      setConnected(false)
    })

    socketInstance.on('error', (error: any) => {
      console.error('WebSocket error:', error)
    })

    setSocket(socketInstance)

    return () => {
      socketInstance.disconnect()
    }
  }, [])

  const subscribe = useCallback((event: string, handler: (data: any) => void) => {
    if (socket) {
      socket.on(event, handler)
    }
  }, [socket])

  const unsubscribe = useCallback((event: string, handler: (data: any) => void) => {
    if (socket) {
      socket.off(event, handler)
    }
  }, [socket])

  return (
    <WebSocketContext.Provider value={{ socket, connected, subscribe, unsubscribe }}>
      {children}
    </WebSocketContext.Provider>
  )
}