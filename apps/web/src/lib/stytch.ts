import { createStytchUIClient } from '@stytch/react/ui'

const publicToken = import.meta.env.VITE_STYTCH_PUBLIC_TOKEN

if (!publicToken) {
  throw new Error('Missing VITE_STYTCH_PUBLIC_TOKEN. Check your environment configuration.')
}

export const stytch = createStytchUIClient(publicToken)
