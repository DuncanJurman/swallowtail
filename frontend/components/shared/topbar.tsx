'use client'

import { Bell, Search, User, Menu } from 'lucide-react'
import { Button } from '../ui/button'
import { Input } from '../ui/input'

interface TopBarProps {
  onMenuClick?: () => void
}

export function TopBar({ onMenuClick }: TopBarProps) {
  return (
    <header className="flex h-16 items-center justify-between border-b bg-[--color-card] px-4 lg:px-6">
      <div className="flex items-center gap-4">
        {/* Mobile menu button */}
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden"
          onClick={onMenuClick}
        >
          <Menu className="h-5 w-5" />
        </Button>

        {/* Search */}
        <div className="relative hidden sm:block">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[--color-muted-foreground]" />
          <Input
            type="search"
            placeholder="Search..."
            className="pl-9 pr-3 w-64 lg:w-96"
          />
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-4">
        {/* Notifications */}
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-[--color-destructive]" />
        </Button>

        {/* User menu */}
        <Button variant="ghost" size="sm" className="gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[--color-primary] text-[--color-primary-foreground]">
            <User className="h-4 w-4" />
          </div>
          <span className="hidden sm:inline-block">John Doe</span>
        </Button>
      </div>
    </header>
  )
}