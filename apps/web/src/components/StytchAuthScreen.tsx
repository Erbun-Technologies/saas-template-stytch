import { useEffect } from 'react'
import { Link, useNavigate } from '@tanstack/react-router'
import { useAuthStore } from '../stores/auth'
import { StytchLoginCard } from './StytchLoginCard'

interface StytchAuthScreenProps {
  heading: string
  subheading: string
  footerHint: {
    text: string
    linkLabel: string
    linkTo: string
  }
  secondaryLink: {
    label: string
    to: string
  }
}

const copy = {
  login: {
    heading: 'Welcome back',
    subheading: 'Sign in to your account',
  },
  signup: {
    heading: 'Get Started',
    subheading: 'Create your account to get started',
  },
} as const

export function StytchAuthScreen({
  heading,
  subheading,
  footerHint,
  secondaryLink,
}: StytchAuthScreenProps) {
  const navigate = useNavigate()
  const { user, isLoading, hasInitialized, intent, setIntent } = useAuthStore()

  useEffect(() => {
    if (hasInitialized && user && !isLoading) {
      navigate({ to: '/dashboard' })
    }
  }, [user, isLoading, hasInitialized, navigate])

  useEffect(() => {
    const pathname = window.location.pathname
    if (pathname.includes('/signup')) {
      setIntent('signup')
    } else if (pathname.includes('/login')) {
      setIntent('login')
    }
  }, [setIntent])

  const displayHeading = copy[intent]?.heading ?? heading
  const displaySubheading = copy[intent]?.subheading ?? subheading

  return (
    <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center px-4 py-6 sm:px-0">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-foreground">{displayHeading}</h1>
          <p className="text-muted-foreground">{displaySubheading}</p>
        </div>

        <StytchLoginCard />

        <div className="text-center text-sm text-muted-foreground">
          {footerHint.text}{' '}
          <Link
            to={footerHint.linkTo}
            className="text-primary hover:text-primary/80 font-medium transition-colors"
          >
            {footerHint.linkLabel}
          </Link>
        </div>

        <div className="text-center">
          <Link
            to={secondaryLink.to}
            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            {secondaryLink.label}
          </Link>
        </div>
      </div>
    </div>
  )
}

