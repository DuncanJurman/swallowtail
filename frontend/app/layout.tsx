import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { QueryProvider } from '@/providers/query-provider'
import { WebSocketProvider } from '@/providers/websocket-provider'
import { Toaster } from '@/components/ui/toaster'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Swallowtail Dashboard',
  description: 'Autonomous e-commerce platform powered by AI agents',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <QueryProvider>
          <WebSocketProvider>
            {children}
            <Toaster />
          </WebSocketProvider>
        </QueryProvider>
      </body>
    </html>
  )
}