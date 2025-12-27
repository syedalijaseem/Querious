/**
 * NotFoundPage - 404 error page
 */
import { Link } from "react-router-dom";
import { Home, ArrowLeft } from "lucide-react";

export function NotFoundPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--color-bg)] px-4">
      <div className="text-center max-w-md">
        <div className="text-8xl font-bold text-[var(--color-accent)] mb-4">
          404
        </div>
        <h1 className="text-2xl font-semibold text-[var(--color-text-primary)] mb-2">
          Page not found
        </h1>
        <p className="text-[var(--color-text-secondary)] mb-8">
          Sorry, we couldn't find the page you're looking for. It might have
          been moved or deleted.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button
            onClick={() => window.history.back()}
            className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-medium
                       border border-[var(--color-border)] text-[var(--color-text-primary)]
                       hover:bg-[var(--color-surface)] transition-colors"
          >
            <ArrowLeft size={18} />
            Go back
          </button>
          <Link
            to="/"
            className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-medium
                       bg-[var(--color-accent)] text-white
                       hover:bg-[var(--color-accent-hover)] transition-colors"
          >
            <Home size={18} />
            Go home
          </Link>
        </div>
      </div>
    </div>
  );
}
