interface TopBarProps {
  onMenuClick?: () => void
}

export function TopBar({ onMenuClick }: TopBarProps) {
  return (
    <div className="border-b">
      <div className="flex h-16 items-center px-4">
        <button onClick={onMenuClick} className="lg:hidden mr-4">
          <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <h2 className="text-lg font-semibold">Swallowtail</h2>
      </div>
    </div>
  )
}