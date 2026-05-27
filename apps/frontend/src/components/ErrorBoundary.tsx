import type { ErrorComponentProps } from '@tanstack/react-router';
import { ErrorComponent } from '@tanstack/react-router';
import React, { type JSX, type ReactNode } from 'react';

/**
 * Centered error boundary surface used as the router default.
 * @param {ErrorComponentProps} props - Error component props containing error and reset
 * @param {Error} props.error - The error object
 * @param {() => void} props.reset - Reset function to recover from error
 * @returns {JSX.Element} The error boundary component
 */
export function PrettyErrorBoundary({ error, reset }: ErrorComponentProps): JSX.Element {
  return (
    <div className="flex min-h-[60vh] items-center justify-center px-4">
      <div className="max-w-2xl w-full space-y-4 rounded-3xl border border-white/10 bg-white/5 p-8 text-center shadow-2xl backdrop-blur">
        <div className="inline-flex h-12 items-center justify-center rounded-full bg-gradient-to-r from-red-500 to-amber-500 px-5 text-sm font-semibold text-white shadow-lg shadow-red-900/30">
          Something went wrong
        </div>
        <div className="space-y-2 text-left">
          <div className="text-xs font-semibold uppercase tracking-[0.3em] text-red-100/70">Error details</div>
          <pre className="overflow-auto rounded-2xl bg-black/60 p-4 text-left text-xs text-red-100/90">{String(error)}</pre>
        </div>
        <button
          type="button"
          onClick={reset}
          className="inline-flex items-center justify-center gap-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-500/20 transition hover:-translate-y-[1px] hover:shadow-purple-500/25"
        >
          Try again
        </button>
      </div>
    </div>
  );
}

/**
 * Wrapper component to reuse TanStack's built-in ErrorComponent styles inside the pretty card.
 * @param {object} props - Component props
 * @param {ReactNode} props.children - Child components to render inside the shell
 * @returns {JSX.Element} The error shell component
 */
export function PrettyErrorShell({ children }: { children: ReactNode }): JSX.Element {
  return (
    <div className="flex min-h-[60vh] items-center justify-center px-4">
      <div className="max-w-2xl w-full space-y-4 rounded-3xl border border-white/10 bg-white/5 p-8 text-center shadow-2xl backdrop-blur">
        {children}
      </div>
    </div>
  );
}

/**
 * Fallback that keeps the built-in router ErrorComponent but centers it.
 * @param {object} props - Component props
 * @param {unknown} props.error - The error to display
 * @returns {JSX.Element} The centered error component
 */
export function DefaultCenteredError({ error }: { error: unknown }): JSX.Element {
  return (
    <PrettyErrorShell>
      <ErrorComponent error={error} />
    </PrettyErrorShell>
  );
}

interface ClientBoundaryState {
  error: Error | null;
}

/**
 * Generic React error boundary for client hydration/runtime errors.
 */
export class ClientErrorBoundary extends React.Component<{ children: ReactNode }, ClientBoundaryState> {
  state: ClientBoundaryState = { error: null };

  /**
   * Update state when an error is caught.
   * @param {Error} error - The error object caught
   * @returns {ClientBoundaryState} New state with error
   */
  static getDerivedStateFromError(error: Error): ClientBoundaryState {
    return { error };
  }

  /**
   * Handle the caught error with logging.
   * @param {Error} error - The error object
   * @param {React.ErrorInfo} info - React error info
   * @returns {void}
   */
  override componentDidCatch(error: Error, info: React.ErrorInfo): void {
    console.error('Client boundary caught error', error, info);
  }

  /**
   * Reset the error state and reload the page.
   * @returns {void}
   */
  handleReset = (): void => {
    this.setState({ error: null });
    window.location.reload();
  };

  /**
   * Render the component, showing error UI if an error occurred.
   * @returns {React.ReactNode} The component output
   */
  override render(): React.ReactNode {
    if (this.state.error) {
      return (
        <PrettyErrorBoundary error={this.state.error} reset={this.handleReset} />
      );
    }
    return this.props.children;
  }
}
