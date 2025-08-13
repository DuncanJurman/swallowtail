'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '../../lib/utils'
import {
  LayoutDashboard,
  Building2,
  Settings,
  HelpCircle,
  LogOut,
  ChevronLeft,
  ChevronRight,
  FileText,
  Shield,
  TestTube,
} from 'lucide-react'
import { Button } from '../ui/button'
import { useState } from 'react'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Instances', href: '/instances', icon: Building2 },
  { name: 'Test TikTok', href: '/test-tiktok', icon: TestTube },
  { name: 'Settings', href: '/settings', icon: Settings },
]

const bottomNavigation = [
  { name: 'Privacy Policy', href: '/privacy', icon: Shield },
  { name: 'Terms of Service', href: '/terms', icon: FileText },
  { name: 'Help', href: '/help', icon: HelpCircle },
  { name: 'Logout', href: '/logout', icon: LogOut },
]

export function Sidebar() {
  const pathname = usePathname()
  const [collapsed, setCollapsed] = useState(false)

  return (
    <div
      className={cn(
        'flex h-full flex-col border-r bg-card transition-all duration-300',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Logo */}
      <div className="flex h-16 items-center justify-between border-b px-4">
        {!collapsed && (
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-primary" />
            <span className="text-xl font-semibold">Swallowtail</span>
          </Link>
        )}
        {collapsed && (
          <Link href="/dashboard" className="mx-auto">
            <div className="h-8 w-8 rounded-lg bg-primary" />
          </Link>
        )}
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 space-y-1 p-4">
        {navigation.map((item) => {
          const isActive = pathname.startsWith(item.href)
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-secondary text-secondary-foreground'
                  : 'text-muted-foreground hover:bg-secondary/50 hover:text-secondary-foreground'
              )}
            >
              <item.icon className="h-5 w-5 flex-shrink-0" />
              {!collapsed && <span>{item.name}</span>}
            </Link>
          )
        })}
      </nav>

      {/* Bottom Navigation */}
      <div className="border-t p-4">
        <div className="space-y-1">
          {bottomNavigation.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-[--color-muted-foreground] transition-colors hover:bg-[--color-secondary]/50 hover:text-[--color-secondary-foreground]"
            >
              <item.icon className="h-5 w-5 flex-shrink-0" />
              {!collapsed && <span>{item.name}</span>}
            </Link>
          ))}
        </div>
      </div>

      {/* Collapse Toggle */}
      <div className="border-t p-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setCollapsed(!collapsed)}
          className="w-full justify-center"
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>
    </div>
  )
}