import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Terms of Service - Swallowtail',
  description: 'Terms of Service for Swallowtail - AI-powered business management platform',
}

export default function TermsOfService() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-12 max-w-4xl">
        <h1 className="text-4xl font-bold mb-8">Terms of Service</h1>
        
        <div className="prose prose-gray max-w-none space-y-6">
          <p className="text-muted-foreground">
            Effective Date: {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
          </p>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">1. Agreement to Terms</h2>
            <p>
              By accessing or using Swallowtail&apos;s services, you agree to be bound by these Terms of Service (&quot;Terms&quot;). If you disagree with any part of these terms, you may not access our services.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">2. Description of Service</h2>
            <p>
              Swallowtail is an AI-powered business management platform that enables users to:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Manage multiple business instances through AI agents</li>
              <li>Automate content creation and posting across social media platforms</li>
              <li>Analyze performance metrics and optimize strategies</li>
              <li>Execute complex business tasks through natural language commands</li>
              <li>Integrate with third-party platforms including TikTok, Instagram, and others</li>
            </ul>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">3. User Accounts</h2>
            <h3 className="text-xl font-semibold">3.1 Registration</h3>
            <p>
              To use our services, you must create an account providing accurate, complete, and current information. You are responsible for maintaining the confidentiality of your account credentials.
            </p>
            
            <h3 className="text-xl font-semibold">3.2 Account Responsibilities</h3>
            <ul className="list-disc pl-6 space-y-2">
              <li>You are responsible for all activities under your account</li>
              <li>You must notify us immediately of any unauthorized use</li>
              <li>You may not use another&apos;s account without permission</li>
              <li>You must be at least 18 years old to use our services</li>
            </ul>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">4. Acceptable Use Policy</h2>
            <p>You agree not to use our services to:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Violate any laws or regulations</li>
              <li>Infringe on intellectual property rights</li>
              <li>Distribute spam, malware, or harmful content</li>
              <li>Harass, abuse, or harm others</li>
              <li>Attempt to gain unauthorized access to our systems</li>
              <li>Violate third-party platform terms (including TikTok&apos;s Terms of Service)</li>
              <li>Engage in any activity that disrupts our services</li>
            </ul>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">5. Third-Party Platform Integration</h2>
            <h3 className="text-xl font-semibold">5.1 Platform Compliance</h3>
            <p>
              When using our services to interact with third-party platforms (TikTok, Instagram, etc.), you must comply with their respective terms of service and policies.
            </p>
            
            <h3 className="text-xl font-semibold">5.2 Authorization</h3>
            <p>
              By connecting your accounts, you authorize us to access and perform actions on these platforms as directed by you through our AI agents.
            </p>
            
            <h3 className="text-xl font-semibold">5.3 Platform Changes</h3>
            <p>
              We are not responsible for changes to third-party platforms that may affect our integration capabilities.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">6. AI Agent Usage</h2>
            <p>Our AI agents are designed to assist with business tasks. You acknowledge that:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>AI-generated content should be reviewed before publication</li>
              <li>You remain responsible for all content posted through our platform</li>
              <li>AI agents operate based on your instructions and configured parameters</li>
              <li>Results may vary and are not guaranteed</li>
            </ul>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">7. Intellectual Property</h2>
            <h3 className="text-xl font-semibold">7.1 Our Property</h3>
            <p>
              The Swallowtail platform, including all software, designs, and content, is owned by us and protected by intellectual property laws.
            </p>
            
            <h3 className="text-xl font-semibold">7.2 Your Content</h3>
            <p>
              You retain ownership of content you create or upload. By using our services, you grant us a license to use, store, and process your content as necessary to provide our services.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">8. Payment Terms</h2>
            <p>
              If you subscribe to paid services:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Fees are billed in advance on a subscription basis</li>
              <li>All payments are non-refundable unless required by law</li>
              <li>We may change fees with 30 days&apos; notice</li>
              <li>You authorize automatic renewal unless cancelled</li>
            </ul>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">9. Limitation of Liability</h2>
            <p>
              TO THE MAXIMUM EXTENT PERMITTED BY LAW, SWALLOWTAIL SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS OR REVENUES, WHETHER INCURRED DIRECTLY OR INDIRECTLY.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">10. Indemnification</h2>
            <p>
              You agree to indemnify and hold harmless Swallowtail from any claims, damages, or expenses arising from your use of our services or violation of these Terms.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">11. Termination</h2>
            <p>
              We may terminate or suspend your account immediately, without prior notice, for any reason, including breach of these Terms. Upon termination, your right to use our services will cease immediately.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">12. Modifications to Terms</h2>
            <p>
              We reserve the right to modify these Terms at any time. We will notify users of material changes. Continued use after changes constitutes acceptance of new Terms.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">13. Governing Law</h2>
            <p>
              These Terms shall be governed by and construed in accordance with the laws of the United States, without regard to conflict of law provisions.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">14. Contact Information</h2>
            <p>
              For questions about these Terms, please contact us at:
            </p>
            <div className="pl-6">
              <p>Email: contact@skipper-ecom.com</p>
              <p>Website: https://skipper-ecom.com</p>
            </div>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold mt-8">15. Entire Agreement</h2>
            <p>
              These Terms constitute the entire agreement between you and Swallowtail regarding the use of our services, superseding any prior agreements.
            </p>
          </section>
        </div>
      </div>
    </div>
  )
}