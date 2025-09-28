import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '../stores/auth'
import { useEffect } from 'react'
import { Button } from '../components/ui/button'
import { User, Mail, CheckCircle, XCircle, Loader2 } from 'lucide-react'
import { stytch } from '../lib/stytch'

// Establish session with backend if not already done
async function establishBackendSession(): Promise<void> {
  // Check if we already have a session cookie by trying a simple request
  try {
    const testResponse = await fetch('http://localhost:8000/auth/me', {
      credentials: 'include',
    })
    if (testResponse.ok) {
      // Session already established
      return
    }
  } catch (error) {
    // Continue to establish session
  }

  // Get session token from Stytch
  const session = stytch.session.getSync()
  if (!session) {
    throw new Error('Session expired - please log in again')
  }

  const tokens = stytch.session.getTokens()
  if (!tokens || !tokens.session_token) {
    throw new Error('Session tokens not available - please log in again')
  }

  // Establish session with backend
  const response = await fetch('http://localhost:8000/auth/session', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({
      session_token: tokens.session_token,
    }),
  })

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Session establishment failed - session may have expired')
    }
    throw new Error(`Session establishment failed: ${response.status}`)
  }
}

// API call to check backend authentication
async function checkBackendAuth(): Promise<{ user: { user_id: string; email: string; name?: string }; authenticated: boolean }> {
  // Ensure backend session is established
  await establishBackendSession()

  const response = await fetch('http://localhost:8000/auth/me', {
    credentials: 'include',
  })

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Authentication failed - session may have expired')
    }
    throw new Error(`Backend auth failed: ${response.status}`)
  }

  return response.json()
}

export const Route = createFileRoute('/dashboard')({
  component: Dashboard,
})

function Dashboard() {
  const { user, hasInitialized } = useAuthStore()
  const navigate = useNavigate()

  // Query to check backend authentication
  const { data: backendAuth, isLoading: backendLoading, error: backendError } = useQuery({
    queryKey: ['backend-auth'],
    queryFn: checkBackendAuth,
    enabled: !!user && hasInitialized, // Only run when user is authenticated on frontend
    retry: (failureCount, error) => {
      // Don't retry on authentication errors - redirect to login instead
      if (error?.message?.includes('session expired') || error?.message?.includes('please log in')) {
        return false
      }
      return failureCount < 2
    },
  })

  // Handle session expiry - redirect to login
  useEffect(() => {
    if (backendError?.message?.includes('session expired') || backendError?.message?.includes('please log in')) {
      navigate({ to: '/login' })
    }
  }, [backendError, navigate])

  // Redirect if not logged in
  useEffect(() => {
    if (hasInitialized && !user) {
      navigate({ to: '/login' })
    }
  }, [user, hasInitialized, navigate])

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-8rem)]">
        <div className="text-muted-foreground">
          {hasInitialized ? 'Redirecting...' : 'Checking your dashboard...'}
        </div>
      </div>
    )
  }


  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Welcome back to your workspace
          </p>
        </div>

        {/* Authentication Status Cards */}
        <div className="grid gap-6 md:grid-cols-2 mb-6">
          {/* Frontend Auth Status */}
          <div className="bg-card rounded-lg border border-border p-6">
            <h2 className="text-xl font-semibold text-foreground mb-4 flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              Frontend Authentication
            </h2>
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <Mail className="h-4 w-4 text-muted-foreground" />
                <div>
                  <div className="text-sm text-muted-foreground">Email</div>
                  <div className="text-foreground font-medium">
                    {user.emails[0]?.email || 'No email'}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <User className="h-4 w-4 text-muted-foreground" />
                <div>
                  <div className="text-sm text-muted-foreground">User ID</div>
                  <div className="text-foreground font-mono text-sm">
                    {user.user_id}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Backend Auth Status */}
          <div className="bg-card rounded-lg border border-border p-6">
            <h2 className="text-xl font-semibold text-foreground mb-4 flex items-center gap-2">
              {backendLoading ? (
                <Loader2 className="h-5 w-5 animate-spin text-blue-500" />
              ) : backendAuth?.authenticated ? (
                <CheckCircle className="h-5 w-5 text-green-500" />
              ) : backendError ? (
                <XCircle className="h-5 w-5 text-red-500" />
              ) : (
                <div className="h-5 w-5 rounded-full border-2 border-muted-foreground animate-pulse" />
              )}
              Backend Authentication
            </h2>
            {backendLoading ? (
              <div className="text-muted-foreground">Validating session with backend...</div>
            ) : backendError ? (
              <div className="text-red-600 dark:text-red-400">
                <div className="font-medium">Session validation failed</div>
                <div className="text-sm mt-1">
                  {backendError.message.includes('session expired') || backendError.message.includes('please log in')
                    ? 'Redirecting to login...'
                    : backendError.message
                  }
                </div>
              </div>
            ) : backendAuth ? (
              <div className="space-y-3">
                <div className="text-green-600 dark:text-green-400 font-medium">
                  ✅ Backend authentication successful
                </div>
                <div className="flex items-center gap-3">
                  <Mail className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <div className="text-sm text-muted-foreground">Verified Email</div>
                    <div className="text-foreground font-medium">
                      {backendAuth.user.email}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <User className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <div className="text-sm text-muted-foreground">Verified User ID</div>
                    <div className="text-foreground font-mono text-sm">
                      {backendAuth.user.user_id}
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-muted-foreground">Preparing session validation...</div>
            )}
          </div>
        </div>

        {/* Content Placeholder */}
        <div className="grid gap-6 md:grid-cols-2">
          <div className="bg-card rounded-lg border border-border p-6">
            <h3 className="text-lg font-semibold text-foreground mb-3">
              Your Stuff
            </h3>
            <p className="text-muted-foreground">
              Have some stuff here
            </p>
            <Button className="mt-4" disabled>
              Coming Soon
            </Button>
          </div>

          <div className="bg-card rounded-lg border border-border p-6">
            <h3 className="text-lg font-semibold text-foreground mb-3">
              Some Stats
            </h3>
            <p className="text-muted-foreground">
              Have some stats here
            </p>
            <Button className="mt-4" disabled>
              Coming Soon
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}