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

      // Set up message listener for callback
      this.messageListener = (event: MessageEvent) => {
        // Verify origin (adjust for your domain)
        const allowedOrigins = [
          process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3001',
          'https://skipper-ecom.com'
        ]

        if (!allowedOrigins.includes(event.origin)) {
          return
        }

        // Handle callback message
        if (event.data.type === 'tiktok-callback-success') {
          this.cleanup()
          if (onSuccess) {
            onSuccess(event.data.payload as TikTokCallbackSuccess)
          }
        } else if (event.data.type === 'tiktok-callback-error') {
          this.cleanup()
          if (onError) {
            onError(event.data.payload as TikTokCallbackError)
          }
        }
      }

      window.addEventListener('message', this.messageListener)

      // Check if popup was closed manually
      const checkInterval = setInterval(() => {
        if (this.popup && this.popup.closed) {
          clearInterval(checkInterval)
          this.cleanup()
          if (onError) {
            onError({
              error: 'popup_closed',
              error_description: 'The authentication popup was closed before completing'
            })
          }
        }
      }, 500)

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
    if (this.popup && !this.popup.closed) {
      this.popup.close()
    }
    this.popup = null

    if (this.messageListener) {
      window.removeEventListener('message', this.messageListener)
      this.messageListener = null
    }

    // Clean up session storage
    sessionStorage.removeItem('tiktok_oauth_state')
    sessionStorage.removeItem('tiktok_oauth_instance')
  }
}