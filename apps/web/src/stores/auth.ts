import { create } from 'zustand'
import type { Session, User } from '@stytch/core/public'
import { stytch } from '../lib/stytch'
import { sessionManager } from '../lib/sessionManager'

type AuthIntent = 'login' | 'signup'

type SyncPayload = {
  user: User | null
  session: Session | null
  isLoading: boolean
  hasInitialized: boolean
}

interface AuthState {
  user: User | null
  session: Session | null
  isLoading: boolean
  hasInitialized: boolean
  intent: AuthIntent
  syncFromStytch: (payload: SyncPayload) => void
  setIntent: (intent: AuthIntent) => void
  logout: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  session: null,
  isLoading: true,
  hasInitialized: false,
  intent: 'login',
  syncFromStytch: ({ user, session, isLoading, hasInitialized }) => {
    set({ user, session, isLoading, hasInitialized })
  },
  setIntent: (intent) => set({ intent }),
  logout: async () => {
    try {
      // Stop session extension before logout
      sessionManager.stopExtension()

      // Revoke Stytch session (this handles both server revocation and cookie clearing)
      await stytch.session.revoke()

      // Clear local state
      set({ user: null, session: null })

      // Optional: Notify backend that user logged out (for analytics/logging only)
      // This is not security-critical since Stytch revoke already handled logout
      try {
        await fetch('http://localhost:8000/auth/logout', {
          method: 'POST',
          credentials: 'include',
        })
      } catch (error) {
        // Backend notification is optional - don't fail logout if this fails
        console.warn('Backend logout notification failed:', error)
      }
    } catch (error) {
      console.error('Logout error:', error)
      // Even if revoke fails, clear local state to ensure user is logged out locally
      set({ user: null, session: null })
    }
  },
}))
