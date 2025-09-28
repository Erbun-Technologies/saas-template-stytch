import { useEffect, useMemo, useState } from 'react'
import { StytchLogin } from '@stytch/react'
import type { StytchLoginConfig, StyleConfig } from '@stytch/vanilla-js'
import { Products } from '@stytch/core/public'
import { useTheme } from 'next-themes'

function getOrigin() {
  if (typeof window === 'undefined') {
    return ''
  }

  return window.location.origin
}

export function StytchLoginCard() {
  const origin = getOrigin()
  const { resolvedTheme } = useTheme()
  const [palette, setPalette] = useState(() =>
    resolvedTheme === 'dark'
      ? {
          surface: '#111827',
          surfaceMuted: '#1f2937',
          border: '#1e293b',
          text: '#e2e8f0',
          mutedText: '#94a3b8',
          primary: '#2563eb',
          primaryText: '#e2e8f0',
          divider: '#1e293b',
        }
      : {
          surface: '#ffffff',
          surfaceMuted: '#f8fafc',
          border: '#e2e8f0',
          text: '#0f172a',
          mutedText: '#4b5563',
          primary: '#2563eb',
          primaryText: '#ffffff',
          divider: '#e2e8f0',
        },
  )

  useEffect(() => {
    if (typeof window === 'undefined') {
      return
    }

    const getValue = (name: string, fallback: string) => {
      const value = getComputedStyle(document.documentElement).getPropertyValue(name)
      return value ? `hsl(${value.trim()})` : fallback
    }

    setPalette({
      surface: getValue('--card', resolvedTheme === 'dark' ? '#111827' : '#ffffff'),
      surfaceMuted: getValue('--secondary', resolvedTheme === 'dark' ? '#1f2937' : '#f8fafc'),
      border: getValue('--border', resolvedTheme === 'dark' ? '#1e293b' : '#e2e8f0'),
      text: getValue('--card-foreground', resolvedTheme === 'dark' ? '#e2e8f0' : '#0f172a'),
      mutedText: getValue('--muted-foreground', resolvedTheme === 'dark' ? '#94a3b8' : '#4b5563'),
      primary: getValue('--primary', '#2563eb'),
      primaryText: getValue('--primary-foreground', resolvedTheme === 'dark' ? '#0f172a' : '#ffffff'),
      divider: getValue('--border', resolvedTheme === 'dark' ? '#1e293b' : '#e2e8f0'),
    })
  }, [resolvedTheme])

  const config = useMemo<StytchLoginConfig>(() => {
    const passwordOptions = origin
      ? {
          resetPasswordRedirectURL: `${origin}/reset-password`,
        }
      : undefined

    return {
      products: [Products.passwords],
      sessionOptions: {
        sessionDurationMinutes: 60,
      },
      passwordOptions,
    }
  }, [origin])

  const styles = useMemo<StyleConfig>(
    () => ({
      container: {
        width: '100%',
        backgroundColor: palette.surface,
        borderColor: palette.border,
        borderRadius: '16px',
      },
      colors: {
        primary: palette.primary,
        secondary: palette.mutedText,
        success: '#22c55e',
        error: '#ef4444',
      },
      inputs: {
        backgroundColor: palette.surfaceMuted,
        textColor: palette.text,
        placeholderColor: palette.mutedText,
        borderColor: palette.border,
        borderRadius: '12px',
      },
      buttons: {
        primary: {
          backgroundColor: palette.primary,
          textColor: palette.primaryText,
          borderColor: palette.primary,
          borderRadius: '12px',
        },
        secondary: {
          backgroundColor: palette.surfaceMuted,
          textColor: palette.text,
          borderColor: palette.border,
          borderRadius: '12px',
        },
        disabled: {
          backgroundColor: palette.surfaceMuted,
          textColor: palette.mutedText,
          borderColor: palette.border,
          borderRadius: '12px',
        },
      },
      fontFamily: 'Inter, system-ui, -apple-system, BlinkMacSystemFont, sans-serif',
      divider: {
        borderColor: palette.divider,
      },
    }),
    [palette],
  )

  return (
    <div className="bg-card border border-border rounded-xl shadow-sm p-6">
      <StytchLogin config={config} styles={styles} />
    </div>
  )
}

