import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Privacy Policy - Swallowtail',
  description: 'Privacy Policy for Swallowtail - AI-powered business management platform',
}

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-12 max-w-4xl">
        <h1 className="text-4xl font-bold mb-8">Privacy Policy</h1>
        
        <div className="prose prose-gray max-w-none space-y-6">
          <p className="text-muted-foreground">
            Effective Date: {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
          </p>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">1. Introduction</h2>
            <p>
              Welcome to Swallowtail (&quot;we,&quot; &quot;our,&quot; or &quot;us&quot;). We are committed to protecting your personal information and your right to privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our AI-powered business management platform and services.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">2. Information We Collect</h2>
            
            <h3 className="text-xl font-semibold">2.1 Information You Provide</h3>
            <ul className="list-disc pl-6 space-y-2">
              <li>Account information (name, email, business details)</li>
              <li>Business instance data (business profiles, products, content)</li>
              <li>Task descriptions and communications with AI agents</li>
              <li>Payment and billing information</li>
            </ul>

            <h3 className="text-xl font-semibold">2.2 Third-Party Platform Data</h3>
            <p>When you connect your social media accounts (including TikTok), we collect:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Account identifiers and profile information</li>
              <li>Content you authorize us to post on your behalf</li>
              <li>Analytics and engagement data</li>
              <li>Access tokens for platform APIs</li>
            </ul>

            <h3 className="text-xl font-semibold">2.3 TikTok-Specific Data Collection</h3>
            <p>For TikTok integration, we specifically collect:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>TikTok user ID and username</li>
              <li>OAuth access and refresh tokens</li>
              <li>Content posting permissions</li>
              <li>Business account information (if applicable)</li>
              <li>Video performance metrics</li>
            </ul>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">3. How We Use Your Information</h2>
            <p>We use the collected information to:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Provide and maintain our services</li>
              <li>Execute AI-powered tasks on your behalf</li>
              <li>Post content to your connected social media accounts</li>
              <li>Analyze performance and provide insights</li>
              <li>Improve our AI agents and services</li>
              <li>Communicate with you about updates and features</li>
              <li>Ensure compliance with platform policies</li>
            </ul>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">4. Data Storage and Security</h2>
            <p>
              We implement industry-standard security measures to protect your data:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Encryption of sensitive data in transit and at rest</li>
              <li>Secure storage of API tokens and credentials</li>
              <li>Regular security audits and updates</li>
              <li>Access controls and authentication measures</li>
              <li>Isolated instance architecture for data separation</li>
            </ul>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">5. Data Sharing and Disclosure</h2>
            <p>We do not sell your personal information. We may share your data:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>With connected platforms (TikTok, Instagram, etc.) as authorized by you</li>
              <li>With service providers who assist in our operations</li>
              <li>To comply with legal obligations or protect rights</li>
              <li>With your explicit consent</li>
            </ul>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">6. Your Rights and Choices</h2>
            <p>You have the right to:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Access and update your personal information</li>
              <li>Delete your account and associated data</li>
              <li>Revoke platform connections at any time</li>
              <li>Opt-out of marketing communications</li>
              <li>Request data portability</li>
              <li>Lodge complaints with supervisory authorities</li>
            </ul>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">7. Data Retention</h2>
            <p>
              We retain your data for as long as necessary to provide our services and comply with legal obligations. When you delete your account, we will delete or anonymize your personal information within 30 days, except where retention is required by law.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">8. Children&apos;s Privacy</h2>
            <p>
              Our services are not intended for users under 18 years of age. We do not knowingly collect personal information from children.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">9. International Data Transfers</h2>
            <p>
              Your information may be transferred to and processed in countries other than your own. We ensure appropriate safeguards are in place for such transfers.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">10. Updates to This Policy</h2>
            <p>
              We may update this Privacy Policy periodically. We will notify you of material changes via email or through our platform.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">11. Contact Us</h2>
            <p>
              If you have questions about this Privacy Policy or our data practices, please contact us at:
            </p>
            <div className="pl-6">
              <p>Email: contact@skipper-ecom.com</p>
              <p>Website: https://skipper-ecom.com</p>
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}