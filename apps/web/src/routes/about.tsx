import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/about')({
  component: About,
})

function About() {
  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="max-w-3xl">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">About SaaS Template</h1>
        <div className="prose prose-lg text-gray-600">
          <p>
            This is a modern SaaS application template designed to help you learn authentication 
            and user management patterns. This template demonstrates:
          </p>
          <ul className="list-disc list-inside mt-4 space-y-2">
            <li>FastAPI backend with CORS configuration</li>
            <li>React frontend with TanStack Router</li>
            <li>TypeScript shared types between frontend and backend</li>
            <li>Docker Compose for local development</li>
            <li>Modern tooling with pnpm workspaces</li>
          </ul>
          <p className="mt-6">
            Ready to add authentication? This setup provides the foundation for integrating 
            Stytch or other auth providers.
          </p>
        </div>
      </div>
    </div>
  )
}
