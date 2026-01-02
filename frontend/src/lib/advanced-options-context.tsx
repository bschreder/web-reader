import { createContext, useContext, useState, ReactNode, JSX } from 'react';

/**
 * Advanced options state interface.
 */
export interface AdvancedOptionsState {
  searchEngine: 'duckduckgo' | 'bing' | 'google' | 'custom';
  maxResults: number;
  safeMode: boolean;
  maxDepth: number;
  sameDomainOnly: boolean;
  allowExternalLinks: boolean;
  maxPages: number;
  timeBudget: number;
}

/**
 * Advanced options context interface.
 */
interface AdvancedOptionsContextValue extends AdvancedOptionsState {
  setSearchEngine: (value: 'duckduckgo' | 'bing' | 'google' | 'custom') => void;
  setMaxResults: (value: number) => void;
  setSafeMode: (value: boolean) => void;
  setMaxDepth: (value: number) => void;
  setSameDomainOnly: (value: boolean) => void;
  setAllowExternalLinks: (value: boolean) => void;
  setMaxPages: (value: number) => void;
  setTimeBudget: (value: number) => void;
  reset: () => void;
}

const defaultState: AdvancedOptionsState = {
  searchEngine: 'duckduckgo',
  maxResults: 10,
  safeMode: true,
  maxDepth: 3,
  sameDomainOnly: false,
  allowExternalLinks: true,
  maxPages: 20,
  timeBudget: 120,
};

const AdvancedOptionsContext = createContext<AdvancedOptionsContextValue | undefined>(undefined);

/**
 * Provider for advanced options context.
 * @param {object} props - Component props
 * @param {ReactNode} props.children - Child components
 * @returns {JSX.Element} The provider component
 */
export function AdvancedOptionsProvider({ children }: { children: ReactNode }): JSX.Element {
  const [searchEngine, setSearchEngine] = useState<'duckduckgo' | 'bing' | 'google' | 'custom'>('duckduckgo');
  const [maxResults, setMaxResults] = useState(10);
  const [safeMode, setSafeMode] = useState(true);
  const [maxDepth, setMaxDepth] = useState(3);
  const [sameDomainOnly, setSameDomainOnly] = useState(false);
  const [allowExternalLinks, setAllowExternalLinks] = useState(true);
  const [maxPages, setMaxPages] = useState(20);
  const [timeBudget, setTimeBudget] = useState(120);

  const reset = (): void => {
    setSearchEngine(defaultState.searchEngine);
    setMaxResults(defaultState.maxResults);
    setSafeMode(defaultState.safeMode);
    setMaxDepth(defaultState.maxDepth);
    setSameDomainOnly(defaultState.sameDomainOnly);
    setAllowExternalLinks(defaultState.allowExternalLinks);
    setMaxPages(defaultState.maxPages);
    setTimeBudget(defaultState.timeBudget);
  };

  return (
    <AdvancedOptionsContext.Provider
      value={{
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
        reset,
      }}
    >
      {children}
    </AdvancedOptionsContext.Provider>
  );
}

/**
 * Hook to use advanced options context.
 * @returns {AdvancedOptionsContextValue} The advanced options context value
 * @throws {Error} If used outside of provider
 */
export function useAdvancedOptions(): AdvancedOptionsContextValue {
  const context = useContext(AdvancedOptionsContext);
  if (!context) {
    throw new Error('useAdvancedOptions must be used within AdvancedOptionsProvider');
  }
  return context;
}
