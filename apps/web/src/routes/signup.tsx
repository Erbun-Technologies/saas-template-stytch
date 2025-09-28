import { createFileRoute } from '@tanstack/react-router'
import { StytchAuthScreen } from '../components/StytchAuthScreen'

export const Route = createFileRoute('/signup')({
  component: Signup,
})

function Signup() {
  return (
    <StytchAuthScreen
      heading="Get Started"
      subheading="Create your account to get started"
      footerHint={{
        text: 'Already have an account?',
        linkLabel: 'Sign in',
        linkTo: '/login',
      }}
      secondaryLink={{
        label: '← Back to home',
        to: '/',
      }}
    />
  )
}