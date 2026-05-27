import { JSX } from 'react';

/**
 * Application header component.
 * @returns {JSX.Element} The header component
 */
export default function Header(): JSX.Element {
  return (
    <header className="h-[25px] bg-gradient-to-r from-blue-900 via-purple-900 to-indigo-900 border-b border-blue-800/50 flex items-center px-6 shadow-lg">
      <div className="flex items-center gap-3">
        <svg data-testid="header-icon" className="w-4 h-4 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <span className="text-xs font-semibold text-blue-100 tracking-wide">Web Reader Research Platform</span>
      </div>
    </header>
  );
}
