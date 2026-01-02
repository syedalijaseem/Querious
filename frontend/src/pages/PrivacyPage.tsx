/**
 * Privacy Policy Page
 */
import { Link } from "react-router-dom";
import { ArrowLeft, Shield, Lock, Eye, Database, Mail } from "lucide-react";

export function PrivacyPage() {
  return (
    <div className="min-h-screen bg-[var(--color-bg)]">
      {/* Header */}
      <header className="border-b border-[var(--color-border)] bg-[var(--color-surface)]">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center gap-4">
          <Link
            to="/"
            className="flex items-center gap-2 text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
          >
            <ArrowLeft size={20} />
            <span>Back to Home</span>
          </Link>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-4 py-12">
        <div className="flex items-center gap-3 mb-8">
          <div className="p-3 rounded-xl bg-[var(--color-accent)]/10">
            <Shield className="text-[var(--color-accent)]" size={28} />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-[var(--color-text-primary)]">
              Privacy Policy
            </h1>
            <p className="text-[var(--color-text-secondary)]">
              Last updated: January 1, 2026
            </p>
          </div>
        </div>

        <div className="space-y-8 text-[var(--color-text-secondary)]">
          {/* Introduction */}
          <section className="p-6 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)]">
            <p className="leading-relaxed">
              At Querious, we take your privacy seriously. This Privacy Policy
              explains how we collect, use, disclose, and safeguard your
              information when you use our document chat application.
            </p>
          </section>

          {/* Data Collection */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <Database size={20} className="text-[var(--color-accent)]" />
              <h2 className="text-xl font-semibold text-[var(--color-text-primary)]">
                Information We Collect
              </h2>
            </div>
            <div className="p-6 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)] space-y-4">
              <div>
                <h3 className="font-medium text-[var(--color-text-primary)] mb-2">
                  Account Information
                </h3>
                <p>
                  When you create an account, we collect your email address and
                  name. If you sign in with Google, we receive basic profile
                  information from Google.
                </p>
              </div>
              <div>
                <h3 className="font-medium text-[var(--color-text-primary)] mb-2">
                  Documents & Content
                </h3>
                <p>
                  We store the PDF documents you upload and the chat
                  conversations you have with those documents. This data is used
                  solely to provide our service.
                </p>
              </div>
              <div>
                <h3 className="font-medium text-[var(--color-text-primary)] mb-2">
                  Usage Data
                </h3>
                <p>
                  We collect anonymous usage statistics to improve our service,
                  such as feature usage and error reports.
                </p>
              </div>
            </div>
          </section>

          {/* Data Usage */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <Eye size={20} className="text-[var(--color-accent)]" />
              <h2 className="text-xl font-semibold text-[var(--color-text-primary)]">
                How We Use Your Data
              </h2>
            </div>
            <div className="p-6 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)]">
              <ul className="space-y-2">
                <li className="flex items-start gap-2">
                  <span className="text-[var(--color-accent)]">•</span>
                  To provide and maintain our service
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[var(--color-accent)]">•</span>
                  To process your documents and generate AI responses
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[var(--color-accent)]">•</span>
                  To communicate with you about your account
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[var(--color-accent)]">•</span>
                  To improve and optimize our service
                </li>
              </ul>
            </div>
          </section>

          {/* Data Security */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <Lock size={20} className="text-[var(--color-accent)]" />
              <h2 className="text-xl font-semibold text-[var(--color-text-primary)]">
                Data Security
              </h2>
            </div>
            <div className="p-6 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)]">
              <p>
                We implement industry-standard security measures including
                encrypted data transmission (HTTPS), secure cloud storage, and
                hashed passwords. Your documents are stored securely and are
                only accessible by you.
              </p>
            </div>
          </section>

          {/* Account Deletion */}
          <section>
            <h2 className="text-xl font-semibold text-[var(--color-text-primary)] mb-4">
              Account Deletion
            </h2>
            <div className="p-6 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)] space-y-4">
              <p>
                When you delete your account, all your personal data is
                immediately and permanently deleted, including:
              </p>
              <ul className="space-y-1">
                <li className="flex items-start gap-2">
                  <span className="text-[var(--color-accent)]">•</span>
                  All uploaded documents and their processed content
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[var(--color-accent)]">•</span>
                  All chat conversations and messages
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[var(--color-accent)]">•</span>
                  All projects and their contents
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[var(--color-accent)]">•</span>
                  All session data and tokens
                </li>
              </ul>
              <p className="text-sm text-[var(--color-text-secondary)]">
                <strong>Note:</strong> To prevent abuse of our free tier, your
                email address is retained in a deactivated state. If you
                re-register with the same email, you will need to upgrade to a
                paid plan to continue using the service.
              </p>
            </div>
          </section>

          {/* Third Parties */}
          <section>
            <h2 className="text-xl font-semibold text-[var(--color-text-primary)] mb-4">
              Third-Party Services
            </h2>
            <div className="p-6 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)]">
              <p className="mb-4">We use the following third-party services:</p>
              <ul className="space-y-2">
                <li className="flex items-start gap-2">
                  <span className="text-[var(--color-accent)]">•</span>
                  <strong>AI Providers</strong> - For generating responses to
                  your questions
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[var(--color-accent)]">•</span>
                  <strong>Cloud Storage</strong> - For securely storing your
                  documents
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[var(--color-accent)]">•</span>
                  <strong>Google OAuth</strong> - For optional social sign-in
                </li>
              </ul>
            </div>
          </section>

          {/* Contact */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <Mail size={20} className="text-[var(--color-accent)]" />
              <h2 className="text-xl font-semibold text-[var(--color-text-primary)]">
                Contact Us
              </h2>
            </div>
            <div className="p-6 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)]">
              <p>
                If you have questions about this Privacy Policy, please contact
                us at{" "}
                <a
                  href="mailto:privacy@querious.dev"
                  className="text-[var(--color-accent)] hover:underline"
                >
                  privacy@querious.dev
                </a>
              </p>
            </div>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-[var(--color-border)] bg-[var(--color-surface)]">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-[var(--color-text-secondary)]">
            <p>© 2025 Querious. All rights reserved.</p>
            <div className="flex gap-6">
              <Link
                to="/privacy"
                className="hover:text-[var(--color-text-primary)] transition-colors"
              >
                Privacy
              </Link>
              <Link
                to="/terms"
                className="hover:text-[var(--color-text-primary)] transition-colors"
              >
                Terms
              </Link>
              <a
                href="mailto:support@querious.dev"
                className="hover:text-[var(--color-text-primary)] transition-colors"
              >
                Contact
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
