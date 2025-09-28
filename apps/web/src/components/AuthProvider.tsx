import { useEffect } from 'react'
import { useStytchSession, useStytchUser } from '@stytch/react'
import { useAuthStore } from '../stores/auth'
import { sessionManager } from '../lib/sessionManager'

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { user, isInitialized: userInitialized } = useStytchUser()
  const { session, isInitialized: sessionInitialized } = useStytchSession()
  const syncFromStytch = useAuthStore((state) => state.syncFromStytch)
  const setIntent = useAuthStore((state) => state.setIntent)

  useEffect(() => {
    const isReady = Boolean(userInitialized && sessionInitialized)
    syncFromStytch({
      user: user ?? null,
      session: session ?? null,
      isLoading: !isReady,
      hasInitialized: isReady,
    })

    // Manage session extension based on auth state
    if (session && isReady) {
      sessionManager.startExtension()
    } else {
      sessionManager.stopExtension()
    }

    if (session?.authentication_factors?.length) {
      const hasPassword = session.authentication_factors.some(
        (factor) => factor.delivery_method === 'knowledge',
      )
      setIntent(hasPassword ? 'login' : 'signup')
    }
  }, [user, session, userInitialized, sessionInitialized, syncFromStytch, setIntent])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      sessionManager.stopExtension()
    }
  }, [])

  return <>{children}</>
}
