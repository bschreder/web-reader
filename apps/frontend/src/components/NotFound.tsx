import { Link } from '@tanstack/react-router';
import type { JSX } from 'react';

/**
 * Centered 404 experience for unmatched routes.
 * @returns {JSX.Element} The not found page component
 */
export default function NotFound(): JSX.Element {
  return (
    <div className="flex h-full items-center justify-center px-4">
      <div className="flex max-w-lg flex-col items-center gap-5 rounded-3xl border border-white/10 bg-white/5 px-10 py-12 text-center shadow-2xl backdrop-blur">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500/90 via-purple-500/80 to-pink-500/80 text-2xl font-black text-white">
          404
        </div>
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-[0.35em] text-blue-100/70">Not Found</p>
          <h1 className="text-2xl font-bold text-white">We couldn&apos;t find that page</h1>
          <p className="text-sm text-neutral-300">
            The link may be broken or the page may have been moved. Try heading back home.
          </p>
        </div>
        <Link
          to="/"
          className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-500/20 transition hover:-translate-y-[1px] hover:shadow-purple-500/25"
        >
          <span aria-hidden="true">↩</span>
          Back to home
        </Link>
      </div>
    </div>
  );
}
