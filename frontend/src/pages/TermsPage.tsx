/**
 * Terms of Service Page
 */
import { Link } from "react-router-dom";
import {
  ArrowLeft,
  FileText,
  AlertCircle,
  CheckCircle,
  XCircle,
} from "lucide-react";

export function TermsPage() {
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
            <FileText className="text-[var(--color-accent)]" size={28} />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-[var(--color-text-primary)]">
              Terms of Service
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
              Welcome to Querious. By using our service, you agree to these
              Terms of Service. Please read them carefully before using our
              document chat application.
            </p>
          </section>

          {/* Acceptance */}
          <section>
            <h2 className="text-xl font-semibold text-[var(--color-text-primary)] mb-4">
              1. Acceptance of Terms
            </h2>
            <div className="p-6 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)]">
              <p>
                By accessing or using Querious, you agree to be bound by these
                Terms of Service and our Privacy Policy. If you do not agree to
                these terms, please do not use our service.
              </p>
            </div>
          </section>

          {/* Service Description */}
          <section>
            <h2 className="text-xl font-semibold text-[var(--color-text-primary)] mb-4">
              2. Service Description
            </h2>
            <div className="p-6 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)]">
              <p>
                Querious is an AI-powered document chat application that allows
                you to upload PDF documents and have conversations about their
                content. We use artificial intelligence to provide answers based
                on your uploaded documents.
              </p>
            </div>
          </section>

          {/* User Responsibilities */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <CheckCircle size={20} className="text-emerald-500" />
              <h2 className="text-xl font-semibold text-[var(--color-text-primary)]">
                3. What You Can Do
              </h2>
            </div>
            <div className="p-6 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)]">
              <ul className="space-y-2">
                <li className="flex items-start gap-2">
                  <span className="text-emerald-500">✓</span>
                  Upload PDF documents you own or have rights to
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-500">✓</span>
                  Chat with your documents for personal or business use
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-500">✓</span>
                  Create projects to organize your documents
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-500">✓</span>
                  Use the service within your plan's limits
                </li>
              </ul>
            </div>
          </section>

          {/* Prohibited Uses */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <XCircle size={20} className="text-red-500" />
              <h2 className="text-xl font-semibold text-[var(--color-text-primary)]">
                4. Prohibited Uses
              </h2>
            </div>
            <div className="p-6 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)]">
              <ul className="space-y-2">
                <li className="flex items-start gap-2">
                  <span className="text-red-500">✗</span>
                  Upload illegal, harmful, or copyrighted content without
                  permission
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-500">✗</span>
                  Attempt to reverse engineer or exploit the service
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-500">✗</span>
                  Share your account credentials with others
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-500">✗</span>
                  Use automated systems to abuse the service
                </li>
              </ul>
            </div>
          </section>

          {/* AI Disclaimer */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <AlertCircle size={20} className="text-amber-500" />
              <h2 className="text-xl font-semibold text-[var(--color-text-primary)]">
                5. AI Disclaimer
              </h2>
            </div>
            <div className="p-6 rounded-xl bg-amber-500/10 border border-amber-500/20">
              <p className="text-[var(--color-text-primary)]">
                Our AI-generated responses are provided for informational
                purposes only. While we strive for accuracy, AI responses may
                contain errors or inaccuracies. Always verify important
                information from original sources. Do not rely solely on AI
                responses for legal, medical, financial, or other critical
                decisions.
              </p>
            </div>
          </section>

          {/* Account Termination */}
          <section>
            <h2 className="text-xl font-semibold text-[var(--color-text-primary)] mb-4">
              6. Account Termination
            </h2>
            <div className="p-6 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)] space-y-4">
              <p>
                We reserve the right to suspend or terminate accounts that
                violate these terms. You may delete your account at any time
                from your Settings page.
              </p>
              <p>
                <strong>Upon deletion:</strong> All your documents, chats,
                projects, and personal data are immediately and permanently
                removed from our systems.
              </p>
              <p className="text-sm text-[var(--color-text-secondary)]">
                <strong>Anti-abuse policy:</strong> To prevent gaming of our
                free tier, your email address is retained in a deactivated
                state. If you choose to return, you may re-register with the
                same email, but will start with an exhausted token balance
                requiring a plan upgrade to continue using the service.
              </p>
            </div>
          </section>

          {/* Changes to Terms */}
          <section>
            <h2 className="text-xl font-semibold text-[var(--color-text-primary)] mb-4">
              7. Changes to Terms
            </h2>
            <div className="p-6 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)]">
              <p>
                We may update these Terms of Service from time to time. We will
                notify you of significant changes via email or through the
                service. Continued use of the service after changes constitutes
                acceptance of the new terms.
              </p>
            </div>
          </section>

          {/* Contact */}
          <section>
            <h2 className="text-xl font-semibold text-[var(--color-text-primary)] mb-4">
              8. Contact
            </h2>
            <div className="p-6 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)]">
              <p>
                For questions about these Terms of Service, please contact us at{" "}
                <a
                  href="mailto:legal@querious.dev"
                  className="text-[var(--color-accent)] hover:underline"
                >
                  legal@querious.dev
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
