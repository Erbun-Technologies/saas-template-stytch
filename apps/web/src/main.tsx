import React from 'react'
import ReactDOM from 'react-dom/client'
import { RouterProvider, createRouter } from '@tanstack/react-router'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { StytchProvider } from '@stytch/react'
import { AuthProvider } from './components/AuthProvider'
import { stytch } from './lib/stytch'
import { routeTree } from './routeTree.gen'
import './index.css'

// Create a new router instance
const router = createRouter({ routeTree })

// Register the router instance for type safety
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}

// Create a client
const queryClient = new QueryClient()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <StytchProvider stytch={stytch}>
        <AuthProvider>
          <RouterProvider router={router} />
        </AuthProvider>
      </StytchProvider>
    </QueryClientProvider>
  </React.StrictMode>,
)
