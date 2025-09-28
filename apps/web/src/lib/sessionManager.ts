import { stytch } from './stytch'

class SessionManager {
  private extensionInterval: NodeJS.Timeout | null = null
  private readonly EXTENSION_INTERVAL = 10 * 60 * 1000 // 10 minutes (check every 10 minutes)
  private readonly EXTENSION_BUFFER = 5 * 60 * 1000 // 5 minutes (extend if expires within 5 minutes)

  /**
   * Start periodic session extension for active sessions
   */
  startExtension() {
    if (this.extensionInterval) {
      console.log('Session extension already running')
      return
    }

    console.log('Starting session extension service')
    this.extensionInterval = setInterval(() => {
      this.extendSessionIfNeeded()
    }, this.EXTENSION_INTERVAL)
  }

  /**
   * Stop periodic session extension
   */
  stopExtension() {
    if (this.extensionInterval) {
      console.log('Stopping session extension service')
      clearInterval(this.extensionInterval)
      this.extensionInterval = null
    }
  }

  /**
   * Check if session needs extension and extend if necessary
   * Follows Stytch documentation pattern for session extension
   */
  private async extendSessionIfNeeded() {
    const session = stytch.session.getSync()
    if (!session) {
      console.log('No active session to extend')
      return
    }

    const expiresAt = new Date(session.expires_at).getTime()
    const now = Date.now()
    const timeUntilExpiry = expiresAt - now

    console.log(`Session expires in ${Math.round(timeUntilExpiry / 1000 / 60)} minutes`)

    // Extend if session expires within buffer time
    if (timeUntilExpiry < this.EXTENSION_BUFFER) {
      try {
        console.log('Extending session for another 60 minutes')

        // This follows the exact pattern from Stytch documentation
        await stytch.session.authenticate({
          session_duration_minutes: 60,
        })

        console.log('Session extended successfully')
      } catch (error) {
        console.error('Session extension failed:', error)
        // Error will be handled by AuthProvider's session change listener
      }
    }
  }

  /**
   * Get current extension status for debugging
   */
  getStatus() {
    return {
      isRunning: this.extensionInterval !== null,
      extensionInterval: this.EXTENSION_INTERVAL,
      extensionBuffer: this.EXTENSION_BUFFER,
    }
  }
}

export const sessionManager = new SessionManager()
