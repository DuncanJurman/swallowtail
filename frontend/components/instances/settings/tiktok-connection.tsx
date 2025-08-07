'use client'

import { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../ui/card'
import { Button } from '../../ui/button'
import { Badge } from '../../ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../../ui/dialog'
import { Input } from '../../ui/input'
import { TikTokOAuth } from '../../../lib/tiktok-oauth'
import { tiktokClient } from '../../../lib/tiktok-client'
import type { TikTokAccount, TikTokCallbackSuccess, TikTokCallbackError } from '../../../types/tiktok'
import { Loader2, AlertCircle, Info, UserX, Clock, ExternalLink } from 'lucide-react'
import { cn } from '../../../lib/utils'

interface TikTokConnectionProps {
  instanceId: string
}

// Custom TikTok icon component
function TikTokIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="currentColor"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.34 6.34 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z" />
    </svg>
  )
}

export function TikTokConnection({ instanceId }: TikTokConnectionProps) {
  const [accounts, setAccounts] = useState<TikTokAccount[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isConnecting, setIsConnecting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showAddAccountDialog, setShowAddAccountDialog] = useState(false)
  const [accountName, setAccountName] = useState('')
  const [disconnectingId, setDisconnectingId] = useState<string | null>(null)

  // Fetch TikTok accounts
  const fetchAccounts = useCallback(async () => {
    try {
      setError(null)
      const fetchedAccounts = await tiktokClient.getAccounts(instanceId)
      setAccounts(fetchedAccounts)
    } catch (err) {
      setError('Failed to load TikTok accounts')
      console.error('Failed to fetch TikTok accounts:', err)
    } finally {
      setIsLoading(false)
    }
  }, [instanceId])

  useEffect(() => {
    fetchAccounts()
  }, [fetchAccounts])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // Reset states when component unmounts
      setShowAddAccountDialog(false)
      setIsConnecting(false)
      setError(null)
      setAccountName('')
    }
  }, [])

  const handleConnect = () => {
    // Reset any previous state before opening dialog
    setError(null)
    setAccountName('')
    setIsConnecting(false)
    setShowAddAccountDialog(true)
  }

  const handleConfirmConnect = async () => {
    // Don't close the dialog yet - keep it open during OAuth flow
    setIsConnecting(true)
    setError(null)

    // Set a timeout to reset state if OAuth takes too long
    const timeoutId = setTimeout(() => {
      setIsConnecting(false)
      setError('Connection timeout. Please try again.')
    }, 60000) // 60 seconds timeout

    await TikTokOAuth.initiateConnection({
      instanceId,
      accountName: accountName.trim() || undefined,
      onSuccess: (data: TikTokCallbackSuccess) => {
        clearTimeout(timeoutId)
        // Close dialog and reset everything on success
        setShowAddAccountDialog(false)
        setIsConnecting(false)
        setAccountName('')
        setError(null)
        // Refresh accounts list with a small delay to ensure backend has processed
        setTimeout(() => {
          fetchAccounts()
        }, 500)
        // Could add a success toast here
      },
      onError: (error: TikTokCallbackError) => {
        clearTimeout(timeoutId)
        // Reset connecting state
        setIsConnecting(false)
        
        // If the user just closed the popup, close the dialog too
        if (error.error === 'popup_closed') {
          setShowAddAccountDialog(false)
          setAccountName('')
          setError(null)
        } else {
          // For other errors, show the error message in the dialog
          setError(error.error_description || 'Failed to connect TikTok account')
        }
      }
    })
  }

  const handleDisconnect = async (accountId: string) => {
    if (!confirm('Are you sure you want to disconnect this TikTok account?')) {
      return
    }

    setDisconnectingId(accountId)
    try {
      await tiktokClient.disconnectAccount(instanceId, accountId)
      // Remove account from list
      setAccounts(accounts.filter(acc => acc.id !== accountId))
      // Could add a success toast here
    } catch (err) {
      setError('Failed to disconnect account')
    } finally {
      setDisconnectingId(null)
    }
  }

  const getStatusColor = (account: TikTokAccount) => {
    if (account.is_active !== 'active' || account.is_token_expired) return 'bg-red-500'
    if (account.is_token_expiring_soon) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  const getStatusText = (account: TikTokAccount) => {
    if (account.is_active !== 'active') return 'Disconnected'
    if (account.is_token_expired) return 'Token Expired'
    if (account.is_token_expiring_soon) return `Expires in ${account.days_until_expiry} days`
    return 'Connected'
  }

  if (isLoading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center p-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </CardContent>
      </Card>
    )
  }

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-black">
                <TikTokIcon className="h-6 w-6 text-white" />
              </div>
              <div>
                <CardTitle>TikTok</CardTitle>
                <CardDescription>
                  Connect your TikTok accounts to post content and manage your presence
                </CardDescription>
              </div>
            </div>
            {process.env.NEXT_PUBLIC_TIKTOK_SANDBOX_MODE === 'true' && (
              <Badge variant="secondary" className="gap-1">
                <Info className="h-3 w-3" />
                Sandbox Mode
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <div className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-800">
              <AlertCircle className="h-4 w-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {accounts.length === 0 ? (
            // Empty state
            <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 text-center">
              <div className="mb-4 rounded-full bg-gray-100 p-3">
                <UserX className="h-8 w-8 text-gray-400" />
              </div>
              <h3 className="mb-2 text-lg font-medium">No TikTok accounts connected</h3>
              <p className="mb-4 max-w-sm text-sm text-muted-foreground">
                Connect your TikTok account to start posting content and growing your audience
              </p>
              <Button onClick={handleConnect} disabled={isConnecting}>
                {isConnecting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Connecting...
                  </>
                ) : (
                  <>
                    <TikTokIcon className="mr-2 h-4 w-4" />
                    Connect TikTok Account
                  </>
                )}
              </Button>
            </div>
          ) : (
            // Connected accounts
            <div className="space-y-3">
              {accounts.map((account) => (
                <div
                  key={account.id}
                  className="flex items-center justify-between rounded-lg border p-4"
                >
                  <div className="flex items-center gap-3">
                    <div className="relative">
                      {account.avatar_url ? (
                        /* eslint-disable-next-line @next/next/no-img-element */
                        <img
                          src={account.avatar_url}
                          alt={account.display_name}
                          className="h-12 w-12 rounded-full"
                        />
                      ) : (
                        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gray-200">
                          <TikTokIcon className="h-6 w-6 text-gray-600" />
                        </div>
                      )}
                      <div
                        className={cn(
                          'absolute -bottom-1 -right-1 h-4 w-4 rounded-full border-2 border-white',
                          getStatusColor(account)
                        )}
                      />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="font-medium">{account.display_name}</h4>
                        {account.user_info?.is_verified && (
                          <Badge variant="secondary" className="h-5 px-1 text-xs">
                            ✓
                          </Badge>
                        )}
                      </div>
                      {account.account_name && (
                        <p className="text-sm text-muted-foreground">{account.account_name}</p>
                      )}
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {getStatusText(account)}
                        </span>
                        {account.user_info?.follower_count && (
                          <span>{account.user_info.follower_count.toLocaleString()} followers</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {account.user_info?.profile_deep_link && (
                      <Button
                        variant="ghost"
                        size="sm"
                        asChild
                      >
                        <a
                          href={account.user_info.profile_deep_link}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDisconnect(account.id)}
                      disabled={disconnectingId === account.id}
                    >
                      {disconnectingId === account.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        'Disconnect'
                      )}
                    </Button>
                  </div>
                </div>
              ))}
              
              <Button
                variant="outline"
                onClick={handleConnect}
                disabled={isConnecting}
                className="w-full"
              >
                {isConnecting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Connecting...
                  </>
                ) : (
                  <>
                    <TikTokIcon className="mr-2 h-4 w-4" />
                    Add Another Account
                  </>
                )}
              </Button>
            </div>
          )}

          {process.env.NEXT_PUBLIC_TIKTOK_SANDBOX_MODE === 'true' && (
            <div className="rounded-lg bg-yellow-50 p-3 text-sm text-yellow-800">
              <div className="flex items-start gap-2">
                <Info className="mt-0.5 h-4 w-4 flex-shrink-0" />
                <div>
                  <p className="font-medium">Sandbox Mode Active</p>
                  <p className="mt-1">
                    Content posted will only be visible to test users. Connect a test account to proceed.
                  </p>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add Account Dialog */}
      <Dialog open={showAddAccountDialog} onOpenChange={(open) => {
        // Allow closing unless actively connecting
        if (!isConnecting || !open) {
          setShowAddAccountDialog(open)
          // Reset form when closing
          if (!open) {
            setAccountName('')
            setError(null)
            setIsConnecting(false)
          }
        }
      }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Connect TikTok Account</DialogTitle>
            <DialogDescription>
              {isConnecting 
                ? 'Connecting to TikTok... Please complete the authorization in the popup window.'
                : 'Add a friendly name to help identify this account (optional)'}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            {error && (
              <div className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-800">
                <AlertCircle className="h-4 w-4 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}
            <div className="space-y-2">
              <label className="text-sm font-medium">Account Name</label>
              <Input
                placeholder="e.g., Main Business Account"
                value={accountName}
                onChange={(e) => setAccountName(e.target.value)}
                disabled={isConnecting}
              />
              <p className="text-xs text-muted-foreground">
                This name is only for your reference and won&apos;t be shown publicly
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => setShowAddAccountDialog(false)}
              disabled={isConnecting}
            >
              Cancel
            </Button>
            <Button 
              onClick={handleConfirmConnect}
              disabled={isConnecting}
            >
              {isConnecting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Connecting...
                </>
              ) : (
                'Continue to TikTok'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}