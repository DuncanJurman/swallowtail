'use client'

import { useEffect, useState, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card'
import { CheckCircle2, XCircle, Loader2 } from 'lucide-react'

function TikTokCallbackContent() {
  const searchParams = useSearchParams()
  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing')
  const [message, setMessage] = useState('Completing TikTok connection...')
  const [countdown, setCountdown] = useState(3)

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code')
      const state = searchParams.get('state')
      const error = searchParams.get('error')
      const errorDescription = searchParams.get('error_description')

      // Handle error case
      if (error) {
        setStatus('error')
        setMessage(errorDescription || 'Authorization was denied')

        // Send error message to parent window if in popup
        if (window.opener) {
          window.opener.postMessage(
            {
              type: 'tiktok-callback-error',
              payload: { error, error_description: errorDescription }
            },
            window.location.origin
          )
        }
        return
      }

      // Verify we have required parameters
      if (!code || !state) {
        setStatus('error')
        setMessage('Missing required parameters')
        return
      }

      try {
        // Make the callback request to backend
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
        const response = await fetch(
          `${apiUrl}/tiktok/callback?code=${encodeURIComponent(code)}&state=${encodeURIComponent(state)}`,
          {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json'
            }
          }
        )

        const data = await response.json()

        if (response.ok && data.status === 'success') {
          setStatus('success')
          setMessage(`Successfully connected ${data.user.display_name}!`)

          // Send success message to parent window if in popup
          if (window.opener) {
            window.opener.postMessage(
              {
                type: 'tiktok-callback-success',
                payload: data
              },
              window.location.origin
            )
          }
        } else {
          throw new Error(data.detail || 'Failed to complete connection')
        }
      } catch (err) {
        setStatus('error')
        setMessage(err instanceof Error ? err.message : 'An unexpected error occurred')

        // Send error message to parent window if in popup
        if (window.opener) {
          window.opener.postMessage(
            {
              type: 'tiktok-callback-error',
              payload: {
                error: 'callback_failed',
                error_description: err instanceof Error ? err.message : 'Callback processing failed'
              }
            },
            window.location.origin
          )
        }
      }
    }

    handleCallback()
  }, [searchParams])

  useEffect(() => {
    // Auto-close countdown
    if (status !== 'processing') {
      const timer = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            // Close window or redirect
            if (window.opener) {
              window.close()
            } else {
              // If not in popup, redirect to instances page
              window.location.href = '/instances'
            }
            return 0
          }
          return prev - 1
        })
      }, 1000)

      return () => clearInterval(timer)
    }
  }, [status])

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4">
            {status === 'processing' && (
              <Loader2 className="h-12 w-12 animate-spin text-primary" />
            )}
            {status === 'success' && (
              <CheckCircle2 className="h-12 w-12 text-green-600" />
            )}
            {status === 'error' && (
              <XCircle className="h-12 w-12 text-red-600" />
            )}
          </div>
          <CardTitle className="text-2xl">
            {status === 'processing' && 'Connecting to TikTok'}
            {status === 'success' && 'Connection Successful!'}
            {status === 'error' && 'Connection Failed'}
          </CardTitle>
          <CardDescription className="mt-2">{message}</CardDescription>
        </CardHeader>
        <CardContent className="text-center">
          {status !== 'processing' && (
            <p className="text-sm text-muted-foreground">
              {countdown > 0
                ? `This window will close in ${countdown} seconds...`
                : 'Closing window...'}
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default function TikTokCallbackPage() {
  return (
    <Suspense fallback={
      <div className="flex min-h-screen items-center justify-center bg-background p-4">
        <Card className="w-full max-w-md">
          <CardContent className="flex items-center justify-center p-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </CardContent>
        </Card>
      </div>
    }>
      <TikTokCallbackContent />
    </Suspense>
  )
}