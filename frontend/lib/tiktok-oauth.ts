import { tiktokClient } from './tiktok-client'
import type { TikTokCallbackSuccess, TikTokCallbackError } from '../types/tiktok'

export interface TikTokOAuthOptions {
  instanceId: string
  accountName?: string
  onSuccess?: (data: TikTokCallbackSuccess) => void
  onError?: (error: TikTokCallbackError) => void
}

export class TikTokOAuth {
  private static popup: Window | null = null
  private static messageListener: ((event: MessageEvent) => void) | null = null
  private static checkInterval: NodeJS.Timeout | null = null
  private static isProcessingCallback: boolean = false
  private static callbackProcessed: boolean = false

  static async initiateConnection({
    instanceId,
    accountName,
    onSuccess,
    onError
  }: TikTokOAuthOptions): Promise<void> {
    try {
      // Clean up any existing popup
      this.cleanup()

      // Get auth URL from backend
      const { auth_url, state } = await tiktokClient.generateAuthUrl(instanceId, accountName)

      // Store state for verification (in production, this should be more secure)
      sessionStorage.setItem('tiktok_oauth_state', state)
      sessionStorage.setItem('tiktok_oauth_instance', instanceId)

      // Open popup window
      const width = 600
      const height = 700
      const left = window.screen.width / 2 - width / 2
      const top = window.screen.height / 2 - height / 2

      this.popup = window.open(
        auth_url,
        'tiktok-oauth',
        `width=${width},height=${height},left=${left},top=${top},toolbar=no,menubar=no,scrollbars=yes,resizable=yes`
      )

      if (!this.popup) {
        throw new Error('Failed to open popup window. Please check your popup blocker settings.')
      }

      // Reset callback flags
      this.isProcessingCallback = false
      this.callbackProcessed = false

      // Set up message listener for callback
      this.messageListener = (event: MessageEvent) => {
        // Debug logging
        console.log('[TikTokOAuth] Message received from origin:', event.origin)
        console.log('[TikTokOAuth] Message type:', event.data?.type)
        
        // Verify origin (adjust for your domain)
        const allowedOrigins = [
          process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3001',
          'https://skipper-ecom.com'
        ]

        if (!allowedOrigins.includes(event.origin)) {
          console.warn('[TikTokOAuth] Origin not allowed:', event.origin, 'Expected one of:', allowedOrigins)
          return
        }

        // Prevent processing duplicate callbacks
        if (this.callbackProcessed) {
          console.log('[TikTokOAuth] Callback already processed, ignoring duplicate')
          return
        }

        // Handle callback message
        if (event.data.type === 'tiktok-callback-success') {
          console.log('[TikTokOAuth] Success callback received')
          this.isProcessingCallback = true
          this.callbackProcessed = true
          
          // Clean up first to prevent race conditions
          this.cleanup()
          
          if (onSuccess) {
            console.log('[TikTokOAuth] Calling onSuccess callback')
            onSuccess(event.data.payload as TikTokCallbackSuccess)
          }
        } else if (event.data.type === 'tiktok-callback-error') {
          console.log('[TikTokOAuth] Error callback received')
          this.isProcessingCallback = true
          this.callbackProcessed = true
          
          this.cleanup()
          
          if (onError) {
            console.log('[TikTokOAuth] Calling onError callback')
            onError(event.data.payload as TikTokCallbackError)
          }
        } else if (event.data.type === 'tiktok-callback-close') {
          console.log('[TikTokOAuth] Close request received')
          // Handle explicit close request from callback page
          this.cleanup()
        }
      }

      window.addEventListener('message', this.messageListener)

      // Check if popup was closed manually
      let popupClosedTime: number | null = null
      const GRACE_PERIOD_MS = 2000 // 2 seconds grace period for messages to arrive
      
      this.checkInterval = setInterval(() => {
        if (this.popup && this.popup.closed) {
          console.log('[TikTokOAuth] Popup detected as closed')
          
          // Don't do anything if we're already processing a callback
          if (this.isProcessingCallback || this.callbackProcessed) {
            console.log('[TikTokOAuth] Already processing/processed callback, stopping interval')
            if (this.checkInterval) {
              clearInterval(this.checkInterval)
              this.checkInterval = null
            }
            return
          }
          
          // First time detecting popup closed - start grace period
          if (popupClosedTime === null) {
            popupClosedTime = Date.now()
            console.log('[TikTokOAuth] Starting grace period for callback messages')
            return
          }
          
          // Check if grace period has expired
          const elapsed = Date.now() - popupClosedTime
          if (elapsed >= GRACE_PERIOD_MS) {
            console.log('[TikTokOAuth] Grace period expired, treating as error')
            this.cleanup()
            if (onError) {
              onError({
                error: 'popup_closed',
                error_description: 'The authentication popup was closed before completing'
              })
            }
          }
        }
      }, 100) // Check more frequently for better responsiveness

    } catch (error) {
      this.cleanup()
      if (onError) {
        onError({
          error: 'auth_failed',
          error_description: error instanceof Error ? error.message : 'Failed to initiate TikTok connection'
        })
      }
    }
  }

  private static cleanup(): void {
    console.log('[TikTokOAuth] Cleanup called')
    
    // Clear the interval first
    if (this.checkInterval) {
      clearInterval(this.checkInterval)
      this.checkInterval = null
    }

    if (this.popup && !this.popup.closed) {
      this.popup.close()
    }
    this.popup = null

    if (this.messageListener) {
      window.removeEventListener('message', this.messageListener)
      this.messageListener = null
    }

    // Reset flags
    this.isProcessingCallback = false
    this.callbackProcessed = false

    // Clean up session storage
    sessionStorage.removeItem('tiktok_oauth_state')
    sessionStorage.removeItem('tiktok_oauth_instance')
  }
}