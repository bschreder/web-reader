import { JSX } from 'react';

/**
 * Props for AdvancedOptions component.
 */
export interface AdvancedOptionsProps {
  searchEngine: 'duckduckgo' | 'bing' | 'google' | 'custom';
  setSearchEngine: (value: 'duckduckgo' | 'bing' | 'google' | 'custom') => void;
  maxResults: number;
  setMaxResults: (value: number) => void;
  safeMode: boolean;
  setSafeMode: (value: boolean) => void;
  maxDepth: number;
  setMaxDepth: (value: number) => void;
  sameDomainOnly: boolean;
  setSameDomainOnly: (value: boolean) => void;
  allowExternalLinks: boolean;
  setAllowExternalLinks: (value: boolean) => void;
  maxPages: number;
  setMaxPages: (value: number) => void;
  timeBudget: number;
  setTimeBudget: (value: number) => void;
}

/**
 * Right sidebar advanced options component.
 * @param {AdvancedOptionsProps} props - Component props
 * @returns {JSX.Element} The advanced options panel
 */
export default function AdvancedOptions(props: AdvancedOptionsProps): JSX.Element {
  const {
    searchEngine,
    setSearchEngine,
    maxResults,
    setMaxResults,
    safeMode,
    setSafeMode,
    maxDepth,
    setMaxDepth,
    sameDomainOnly,
    setSameDomainOnly,
    allowExternalLinks,
    setAllowExternalLinks,
    maxPages,
    setMaxPages,
    timeBudget,
    setTimeBudget,
  } = props;

  return (
    <aside className="w-[35vw] min-w-[300px] border-l border-neutral-800 bg-gradient-to-b from-neutral-900/80 to-neutral-950/80 backdrop-blur-sm overflow-y-auto">
      <div className="p-4 space-y-4 sticky top-0">
        <div className="space-y-1 border-b border-neutral-800 pb-3">
          <div className="flex items-center gap-2">
            <svg data-testid="advanced-options-icon" className="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
            <h2 className="text-sm font-bold text-neutral-200">Advanced Options</h2>
          </div>
          <p className="text-[10px] text-neutral-500">Fine-tune your research parameters</p>
        </div>

        {/* Search Settings */}
        <div className="space-y-3 rounded-lg bg-neutral-900/50 p-3 border border-neutral-800/50">
          <div className="flex items-center gap-2">
            <svg data-testid="search-settings-icon" className="w-3.5 h-3.5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <h3 className="text-xs font-semibold text-blue-300">Search Settings (UC-01)</h3>
          </div>

          <label className="block space-y-1.5">
            <span className="text-xs text-neutral-400">Search Engine</span>
            <select
              data-testid="search-engine-select"
              value={searchEngine}
              onChange={(e) => setSearchEngine(e.target.value as typeof searchEngine)}
              className="w-full rounded-md border border-neutral-700 bg-neutral-900 p-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
            >
              <option value="duckduckgo">🦆 DuckDuckGo (default)</option>
              <option value="bing">🔍 Bing</option>
              <option value="google">🔍 Google</option>
              <option value="custom">⚙️ Custom</option>
            </select>
          </label>

          <label className="block space-y-1.5">
            <span className="text-xs text-neutral-400">Max Search Results</span>
            <input
              data-testid="max-results-input"
              type="number"
              value={maxResults}
              onChange={(e) => setMaxResults(Number(e.target.value))}
              min={1}
              max={50}
              className="w-full rounded-md border border-neutral-700 bg-neutral-900 p-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
            />
            <span className="text-[10px] text-neutral-500">Range: 1-50</span>
          </label>

          <label className="flex items-center gap-2 p-2 rounded hover:bg-neutral-800/50 transition-colors cursor-pointer">
            <input
              data-testid="safe-mode-checkbox"
              type="checkbox"
              checked={safeMode}
              onChange={(e) => setSafeMode(e.target.checked)}
              className="rounded text-blue-600 focus:ring-blue-500"
            />
            <span className="text-xs text-neutral-300">🛡️ Safe Mode (filter unsafe content)</span>
          </label>
        </div>

        {/* Link Following */}
        <div className="space-y-3 rounded-lg bg-neutral-900/50 p-3 border border-neutral-800/50">
          <div className="flex items-center gap-2">
            <svg data-testid="link-following-icon" className="w-3.5 h-3.5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            <h3 className="text-xs font-semibold text-green-300">Link Following (UC-02)</h3>
          </div>

          <label className="block space-y-1.5">
            <span className="text-xs text-neutral-400">Max Link Depth</span>
            <input
              data-testid="max-depth-input"
              type="number"
              value={maxDepth}
              onChange={(e) => setMaxDepth(Number(e.target.value))}
              min={1}
              max={5}
              className="w-full rounded-md border border-neutral-700 bg-neutral-900 p-2 text-sm focus:border-green-500 focus:ring-1 focus:ring-green-500 transition-colors"
            />
            <span className="text-[10px] text-neutral-500">How many links deep to follow (1-5)</span>
          </label>

          <label className="flex items-center gap-2 p-2 rounded hover:bg-neutral-800/50 transition-colors cursor-pointer">
            <input
              data-testid="same-domain-checkbox"
              type="checkbox"
              checked={sameDomainOnly}
              onChange={(e) => setSameDomainOnly(e.target.checked)}
              className="rounded text-green-600 focus:ring-green-500"
            />
            <span className="text-xs text-neutral-300">🔒 Same domain only</span>
          </label>

          <label className="flex items-center gap-2 p-2 rounded hover:bg-neutral-800/50 transition-colors cursor-pointer">
            <input
              data-testid="external-links-checkbox"
              type="checkbox"
              checked={allowExternalLinks}
              onChange={(e) => setAllowExternalLinks(e.target.checked)}
              className="rounded text-green-600 focus:ring-green-500"
            />
            <span className="text-xs text-neutral-300">🌐 Allow external links</span>
          </label>
        </div>

        {/* Limits */}
        <div className="space-y-3 rounded-lg bg-neutral-900/50 p-3 border border-neutral-800/50">
          <div className="flex items-center gap-2">
            <svg data-testid="limits-icon" className="w-3.5 h-3.5 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <h3 className="text-xs font-semibold text-orange-300">Limits (UC-03)</h3>
          </div>

          <label className="block space-y-1.5">
            <span className="text-xs text-neutral-400">Max Pages</span>
            <input
              data-testid="max-pages-input"
              type="number"
              value={maxPages}
              onChange={(e) => setMaxPages(Number(e.target.value))}
              min={1}
              max={50}
              className="w-full rounded-md border border-neutral-700 bg-neutral-900 p-2 text-sm focus:border-orange-500 focus:ring-1 focus:ring-orange-500 transition-colors"
            />
            <span className="text-[10px] text-neutral-500">Maximum pages to visit (1-50)</span>
          </label>

          <label className="block space-y-1.5">
            <span className="text-xs text-neutral-400">Time Budget (seconds)</span>
            <input
              data-testid="time-budget-input"
              type="number"
              value={timeBudget}
              onChange={(e) => setTimeBudget(Number(e.target.value))}
              min={30}
              max={600}
              className="w-full rounded-md border border-neutral-700 bg-neutral-900 p-2 text-sm focus:border-orange-500 focus:ring-1 focus:ring-orange-500 transition-colors"
            />
            <span className="text-[10px] text-neutral-500">Maximum execution time (30-600s)</span>
          </label>
        </div>
      </div>
    </aside>
  );
}
