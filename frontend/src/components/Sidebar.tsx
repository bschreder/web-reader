import { JSX } from 'react';
import { Link, useRouterState } from '@tanstack/react-router';

/**
 * Left sidebar navigation component.
 * @returns {JSX.Element} The sidebar navigation
 */
export default function Sidebar(): JSX.Element {
  const router = useRouterState();
  const currentPath = router.location.pathname;

  return (
    <aside className="w-[15vw] min-w-[150px] border-r border-neutral-800 bg-gradient-to-b from-neutral-900/80 to-neutral-950/80 backdrop-blur-sm">
      <nav className="p-4 space-y-2">
        <div className="text-[10px] uppercase tracking-widest text-neutral-500 font-semibold mb-3 px-2">Navigation</div>
        <Link
          to="/"
          className={`
            block rounded-lg px-4 py-2.5 transition-all duration-200
            ${currentPath === '/' 
              ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-900/50 font-semibold' 
              : 'text-neutral-300 hover:bg-neutral-800 hover:text-white'
            }
          `}
        >
          <div className="flex items-center gap-2">
            <svg data-testid="nav-home-icon" className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            <span className="text-sm">Home</span>
          </div>
        </Link>
        <Link
          to="/history"
          className={`
            block rounded-lg px-4 py-2.5 transition-all duration-200
            ${currentPath === '/history' 
              ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-900/50 font-semibold' 
              : 'text-neutral-300 hover:bg-neutral-800 hover:text-white'
            }
          `}
        >
          <div className="flex items-center gap-2">
            <svg data-testid="nav-history-icon" className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-sm">History</span>
          </div>
        </Link>
      </nav>
    </aside>
  );
}
