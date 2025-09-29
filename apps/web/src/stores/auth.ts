import { create } from 'zustand'
import type { Session, User } from '@stytch/core/public'
import { stytch } from '../lib/stytch'
import { sessionManager } from '../lib/sessionManager'
import { API_BASE_URL, CSRF_COOKIE_NAME, CSRF_HEADER_NAME } from '../lib/config'

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
    console.log('🚪 FRONTEND: Starting logout process...')
    
    try {
      // Stop session extension before logout
      console.log('⏹️ FRONTEND: Stopping session extension...')
      sessionManager.stopExtension()

      // Revoke Stytch session (this handles both server revocation and cookie clearing)
      console.log('🔐 FRONTEND: Revoking Stytch session...')
      await stytch.session.revoke()

      // Clear local state
      console.log('🧹 FRONTEND: Clearing local auth state...')
      set({ user: null, session: null })

      // Optional: Notify backend that user logged out (for analytics/logging only)
      // This is not security-critical since Stytch revoke already handled logout
      try {
        console.log('🌐 FRONTEND: Notifying backend of logout...')
        
        // Get fresh CSRF token for logout request
        const csrfResponse = await fetch(`${API_BASE_URL}/csrf-token`, {
          credentials: 'include',
        })
        
        if (csrfResponse.ok) {
          let csrfToken: string | undefined

          try {
            const csrfData = await csrfResponse.json()
            if (typeof csrfData?.token === 'string' && csrfData.token.length > 0) {
              csrfToken = csrfData.token
            }
          } catch (error) {
            console.warn('⚠️ FRONTEND: Failed to parse CSRF response JSON', error)
          }

          if (!csrfToken) {
            const rawCookie = document.cookie
              .split('; ')
              .find((row) => row.startsWith(`${CSRF_COOKIE_NAME}=`))
            const cookieValue = rawCookie?.split('=')[1]
            if (cookieValue) {
              csrfToken = decodeURIComponent(cookieValue).replace(/^"|"$/g, '')
            }
          }

          if (csrfToken) {
            console.log('🍪 FRONTEND: CSRF token for logout: available')

            await fetch(`${API_BASE_URL}/auth/logout`, {
              method: 'POST',
              headers: {
                [CSRF_HEADER_NAME]: csrfToken,
              },
              credentials: 'include',
            })
            console.log('✅ FRONTEND: Backend logout notification sent')
          } else {
            console.warn('⚠️ FRONTEND: CSRF token not found in response or cookies')
          }
        } else {
          console.warn('⚠️ FRONTEND: Could not get CSRF token for logout')
        }
      } catch (error) {
        // Backend notification is optional - don't fail logout if this fails
        console.warn('⚠️ FRONTEND: Backend logout notification failed:', error)
      }
      
      console.log('✅ FRONTEND: Logout completed successfully')
    } catch (error) {
      console.error('❌ FRONTEND: Logout error:', error)
      // Even if revoke fails, clear local state to ensure user is logged out locally
      set({ user: null, session: null })
    }
  },
}))
