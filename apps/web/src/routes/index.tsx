import { createFileRoute, Link } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import { HealthCheck } from '@saas-template/shared'
import { useAuthStore } from '../stores/auth'
import { Button } from '../components/ui/button'
import { ArrowRight, BookOpen, Users, Zap } from 'lucide-react'
import { API_BASE_URL } from '../lib/config'

async function fetchHealth(): Promise<HealthCheck> {
  const response = await fetch(`${API_BASE_URL}/health`)
  if (!response.ok) {
    throw new Error('Failed to fetch health status')
  }
  return response.json()
}

export const Route = createFileRoute('/')({
  component: Index,
})

function Index() {
  const { data: health, isLoading, error } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
  })
  const { user, hasInitialized } = useAuthStore()

  return (
    <div className="px-4 py-6 sm:px-0">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <h1 className="text-5xl font-bold text-foreground mb-6">
          Welcome to <span className="text-primary">SaaS Template</span>
        </h1>
        <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
          A React + FastAPI SaaS template.
        </p>
        
        {hasInitialized && user ? (
          <div className="space-y-4">
            <p className="text-muted-foreground">
              Welcome back, {user.emails[0]?.email || 'User'}!
            </p>
            <Link to="/dashboard">
              <Button size="lg" className="flex items-center gap-2">
                Go to Dashboard
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
        ) : hasInitialized ? (
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/signup">
              <Button size="lg" className="flex items-center gap-2">
                Get Started
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link to="/login">
              <Button size="lg" variant="outline">
                Sign In
              </Button>
            </Link>
          </div>
        ) : (
          <div className="text-muted-foreground text-center">
            Loading your experience...
          </div>
        )}
      </div>

      {/* Features Section */}
      <div className="grid md:grid-cols-3 gap-8 mb-16">
        <div className="text-center">
          <div className="bg-primary/10 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
            <BookOpen className="h-8 w-8 text-primary" />
          </div>
          <h3 className="text-xl font-semibold text-foreground mb-2">Build things with ready made auth</h3>
          <p className="text-muted-foreground">
            Don't worry about authentication, we've got you covered.
          </p>
        </div>
        
        <div className="text-center">
          <div className="bg-primary/10 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
            <Users className="h-8 w-8 text-primary" />
          </div>
          <h3 className="text-xl font-semibold text-foreground mb-2">User Management</h3>
          <p className="text-muted-foreground">
            Learn modern authentication patterns with secure user accounts.
          </p>
        </div>
        
        <div className="text-center">
          <div className="bg-primary/10 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
            <Zap className="h-8 w-8 text-primary" />
          </div>
          <h3 className="text-xl font-semibold text-foreground mb-2">Modern Stack</h3>
          <p className="text-muted-foreground">
            Built with React, TypeScript, and the latest web technologies.
          </p>
        </div>
      </div>

      {/* Backend Status */}
      <div className="bg-card rounded-lg border border-border p-6 max-w-md mx-auto">
        <h2 className="text-lg font-semibold text-foreground mb-4 text-center">
          System Status
        </h2>
        {isLoading && (
          <div className="text-muted-foreground text-center">Checking backend status...</div>
        )}
        {error && (
          <div className="text-destructive text-center">
            Backend is not responding: {error.message}
          </div>
        )}
        {health && (
          <div className="text-green-600 dark:text-green-400 text-center">
            ✅ Backend is {health.status} (v{health.version})
          </div>
        )}
      </div>
    </div>
  )
}
