import Link from 'next/link'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { ArrowRight, Bot, Zap, Shield, BarChart3, Globe, Users, Building2, Layers } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-primary/5 via-primary/5 to-background px-4 py-20 md:py-32">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center">
            <h1 className="mb-6 text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
              AI-Powered Business Management
            </h1>
            <p className="mx-auto mb-8 max-w-2xl text-lg text-muted-foreground sm:text-xl">
              Manage multiple businesses effortlessly with intelligent AI agents. Connect your TikTok, 
              Instagram, and other social media accounts to automate content creation, posting, and 
              engagement across all your brands from one powerful platform.
            </p>
            <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
              <Link href="/dashboard">
                <Button size="lg" className="gap-2">
                  Get Started <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
              <Link href="#features">
                <Button size="lg" variant="outline">
                  Learn More
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="px-4 py-20 md:py-32">
        <div className="container mx-auto max-w-6xl">
          <div className="mb-12 text-center">
            <h2 className="mb-4 text-3xl font-bold tracking-tight sm:text-4xl">
              One Platform, Multiple Businesses
            </h2>
            <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
              Whether you&apos;re managing 2 or 20 brands, our instance-based architecture keeps each 
              business separate while giving you unified control. Perfect for entrepreneurs running 
              multiple TikTok accounts, Instagram brands, or e-commerce stores.
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            <Card>
              <CardHeader>
                <Bot className="mb-2 h-8 w-8 text-primary" />
                <CardTitle>Intelligent AI Agents</CardTitle>
                <CardDescription>
                  Specialized agents for content, social media, inventory, and more
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Deploy task-specific AI agents that understand your business and execute operations
                  with precision.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Zap className="mb-2 h-8 w-8 text-primary" />
                <CardTitle>Natural Language Control</CardTitle>
                <CardDescription>
                  Simply describe what you need done in plain English
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  No complex interfaces or learning curves. Just tell our AI what you want to
                  accomplish.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Shield className="mb-2 h-8 w-8 text-primary" />
                <CardTitle>Enterprise Security</CardTitle>
                <CardDescription>
                  Bank-level encryption and data protection
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Your business data is encrypted and secure. We never share or sell your
                  information.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <BarChart3 className="mb-2 h-8 w-8 text-primary" />
                <CardTitle>Real-time Analytics</CardTitle>
                <CardDescription>
                  Track performance across all your businesses
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Get insights into sales, engagement, and growth trends with comprehensive
                  dashboards.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Globe className="mb-2 h-8 w-8 text-primary" />
                <CardTitle>Multi-Platform Integration</CardTitle>
                <CardDescription>
                  Connect with Shopify, Instagram, TikTok, and more
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Seamlessly integrate with your existing tools and platforms for unified management.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Users className="mb-2 h-8 w-8 text-primary" />
                <CardTitle>Team Collaboration</CardTitle>
                <CardDescription>
                  Work together with your team efficiently
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Invite team members, assign roles, and collaborate on business operations in
                  real-time.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Multi-Account Management Section */}
      <section className="px-4 py-20 md:py-32 bg-muted/30">
        <div className="container mx-auto max-w-6xl">
          <div className="grid gap-12 lg:grid-cols-2 items-center">
            <div>
              <h2 className="mb-4 text-3xl font-bold tracking-tight sm:text-4xl">
                Built for Multi-Account Management
              </h2>
              <p className="mb-6 text-lg text-muted-foreground">
                Swallowtail&apos;s unique instance-based architecture is designed from the ground up for 
                managing multiple businesses. Each instance is completely isolated with its own:
              </p>
              <ul className="space-y-3 mb-8">
                <li className="flex items-start gap-3">
                  <Building2 className="h-5 w-5 text-primary mt-0.5" />
                  <span className="text-muted-foreground">Dedicated AI agents trained on your brand voice</span>
                </li>
                <li className="flex items-start gap-3">
                  <Globe className="h-5 w-5 text-primary mt-0.5" />
                  <span className="text-muted-foreground">Separate social media account connections</span>
                </li>
                <li className="flex items-start gap-3">
                  <Shield className="h-5 w-5 text-primary mt-0.5" />
                  <span className="text-muted-foreground">Isolated data and analytics</span>
                </li>
                <li className="flex items-start gap-3">
                  <Layers className="h-5 w-5 text-primary mt-0.5" />
                  <span className="text-muted-foreground">Unified dashboard for all your businesses</span>
                </li>
              </ul>
              <Link href="/instances">
                <Button className="gap-2">
                  Explore Instances <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <Card className="bg-background">
                <CardHeader>
                  <CardTitle className="text-lg">E-commerce Instance</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-3">
                    Perfect for online stores with:
                  </p>
                  <ul className="text-sm space-y-1 text-muted-foreground">
                    <li>• Product catalog management</li>
                    <li>• Inventory tracking</li>
                    <li>• Order fulfillment</li>
                    <li>• TikTok Shop integration</li>
                  </ul>
                </CardContent>
              </Card>
              <Card className="bg-background">
                <CardHeader>
                  <CardTitle className="text-lg">Social Media Instance</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-3">
                    Ideal for content creators with:
                  </p>
                  <ul className="text-sm space-y-1 text-muted-foreground">
                    <li>• Multi-platform posting</li>
                    <li>• Content scheduling</li>
                    <li>• Engagement automation</li>
                    <li>• Performance analytics</li>
                  </ul>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-primary px-4 py-20 text-primary-foreground">
        <div className="container mx-auto max-w-4xl text-center">
          <h2 className="mb-4 text-3xl font-bold tracking-tight sm:text-4xl">
            Ready to transform your business?
          </h2>
          <p className="mb-8 text-lg opacity-90">
            Join thousands of entrepreneurs using AI to scale their operations.
          </p>
          <Link href="/dashboard">
            <Button size="lg" variant="secondary" className="gap-2">
              Start Free Trial <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>
    </div>
  )
}