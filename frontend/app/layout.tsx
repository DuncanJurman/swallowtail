import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { QueryProvider } from '../lib/query-client'
import { Footer } from '@/components/shared/footer'

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
})

export const metadata: Metadata = {
  title: 'Swallowtail - AI Business Management',
  description: 'Manage multiple AI-powered business instances',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} font-sans antialiased min-h-screen flex flex-col`}>
        <QueryProvider>
          <div className="flex-1">
            {children}
          </div>
          <Footer />
        </QueryProvider>
      </body>
    </html>
  )
}
