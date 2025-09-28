import { createFileRoute } from '@tanstack/react-router'
import { StytchAuthScreen } from '../components/StytchAuthScreen'

export const Route = createFileRoute('/login')({
  component: Login,
})

function Login() {
  return (
    <StytchAuthScreen
      heading="Welcome back"
      subheading="Sign in to your account"
      footerHint={{
        text: "Don't have an account?",
        linkLabel: 'Sign up',
        linkTo: '/signup',
      }}
      secondaryLink={{
        label: '← Back to home',
        to: '/',
      }}
    />
  )
}