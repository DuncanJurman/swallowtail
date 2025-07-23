import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ArrowRight, Bot, Zap, Globe } from 'lucide-react'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16 text-center">
        <h1 className="mb-6 text-5xl font-bold tracking-tight text-gray-900 sm:text-6xl">
          AI-Powered Business Management
        </h1>
        <p className="mx-auto mb-10 max-w-2xl text-xl text-gray-600">
          Manage multiple businesses with intelligent AI agents that understand your brand and execute
          tasks autonomously.
        </p>
        <div className="flex justify-center gap-4">
          <Button size="lg" className="gap-2">
            Get Started <ArrowRight className="h-4 w-4" />
          </Button>
          <Button size="lg" variant="outline">
            Learn More
          </Button>
        </div>
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-4 py-16">
        <h2 className="mb-12 text-center text-3xl font-bold text-gray-900">
          Powerful Features for Modern Entrepreneurs
        </h2>
        <div className="grid gap-8 md:grid-cols-3">
          <Card>
            <CardHeader>
              <Bot className="mb-4 h-12 w-12 text-primary" />
              <CardTitle>AI Agent Teams</CardTitle>
              <CardDescription>
                Specialized agents work together to manage your business operations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                From content creation to customer service, our AI agents handle complex tasks with
                your brand voice.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Zap className="mb-4 h-12 w-12 text-primary" />
              <CardTitle>Natural Language Control</CardTitle>
              <CardDescription>
                Simply describe what you need in plain English
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                No technical knowledge required. Just tell the system what you want to accomplish.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Globe className="mb-4 h-12 w-12 text-primary" />
              <CardTitle>Multi-Instance Management</CardTitle>
              <CardDescription>
                Run multiple businesses from a single dashboard
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                Each business maintains its own identity, agents, and operational workflows.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* CTA Section */}
      <div className="container mx-auto px-4 py-16 text-center">
        <Card className="mx-auto max-w-2xl bg-primary text-white">
          <CardHeader>
            <CardTitle className="text-2xl">Ready to Transform Your Business?</CardTitle>
            <CardDescription className="text-primary-foreground/80">
              Join thousands of entrepreneurs using AI to scale their operations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button size="lg" variant="secondary" className="gap-2">
              Start Free Trial <ArrowRight className="h-4 w-4" />
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}