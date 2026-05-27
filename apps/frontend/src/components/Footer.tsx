import { JSX } from 'react';

/**
 * Application footer component.
 * @returns {JSX.Element} The footer component
 */
export default function Footer(): JSX.Element {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="h-[25px] bg-gradient-to-r from-neutral-900 via-neutral-950 to-neutral-900 border-t border-neutral-800 flex items-center justify-between px-6">
      <span className="text-[10px] text-neutral-500">© 2025-{currentYear} Web Reader</span>
      <div className="flex items-center gap-3 text-[10px] text-neutral-500">
        <span>Powered by TanStack Start + LangChain + FastMCP + FastAPI + Playwright + Ollama</span>
        <div className="flex items-center gap-1">
          <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
          <span className="text-green-400">Online</span>
        </div>
      </div>
    </footer>
  );
}
