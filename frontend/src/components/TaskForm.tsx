import React, { JSX, useState } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { createTask } from '@lib/api';
import { useAdvancedOptions } from '@lib/advanced-options-context';

/**
 * TaskForm collects question and optional seed URL then creates a task.
 * Uses advanced options from context.
 * @returns {JSX.Element} The task form component
 */
export default function TaskForm(): JSX.Element {
  const navigate = useNavigate();
  const [question, setQuestion] = useState('');
  const [seedUrl, setSeedUrl] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Get advanced options from context
  const {
    searchEngine,
    maxResults,
    safeMode,
    maxDepth,
    maxPages,
    timeBudget,
    sameDomainOnly,
    allowExternalLinks,
    reset: resetAdvancedOptions,
  } = useAdvancedOptions();

  /**
   * Reset the form to its initial state.
   * @returns {void}
   */
  function resetForm(): void {
    setQuestion('');
    setSeedUrl('');
    resetAdvancedOptions();
    setError(null);
    setSubmitting(false);
  }

  /**
   * Handle form submission to create a task.
   * @param {React.FormEvent} e - The form submission event
   * @returns {Promise<void>} A promise that resolves when submission is complete
   */
  async function onSubmit(e: React.FormEvent): Promise<void> {
    e.preventDefault();
    setError(null);
    if (!question.trim()) {
      setError('Question is required');
      return;
    }
    setSubmitting(true);
    try {
      const { id } = await createTask({
        question,
        seedUrl: seedUrl || undefined,
        searchEngine: searchEngine,
        maxResults: maxResults,
        safeMode: safeMode,
        maxDepth: maxDepth,
        maxPages: maxPages,
        timeBudget: timeBudget,
        sameDomainOnly: sameDomainOnly,
        allowExternalLinks: allowExternalLinks,
      });
      navigate({ to: '/tasks/$id', params: { id } });
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-6 max-w-3xl" style={{ marginLeft: '15px' }}>
      <div className="space-y-4">
        <label htmlFor="question-textarea" className="block">
          <div className="flex items-center gap-2 mb-2">
            <svg data-testid="question-icon" className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-sm font-semibold text-neutral-200">Research Question</span>
          </div>
          <textarea
            id="question-textarea"
            name="question-textarea"
            data-testid="question-textarea"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            className="w-full rounded-lg border border-neutral-700 bg-neutral-900/50 p-4 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500/50 transition-all backdrop-blur-sm"
            rows={6}
            required
            placeholder="What would you like to research? e.g., 'What are the latest developments in quantum computing?'"
          />
        </label>
        
        <label htmlFor="seed-url-input" className="block">
          <div className="flex items-center gap-2 mb-2">
            <svg data-testid="seed-url-icon" className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            <span className="text-sm font-semibold text-neutral-200">Seed URL</span>
            <span className="text-xs text-neutral-500">(optional)</span>
          </div>
          <input
            id="seed-url-input"
            name="seed-url-input"
            data-testid="seed-url-input"
            value={seedUrl}
            onChange={(e) => setSeedUrl(e.target.value)}
            type="url"
            placeholder="https://example.com"
            className="w-full rounded-lg border border-neutral-700 bg-neutral-900/50 p-3 text-sm focus:border-green-500 focus:ring-2 focus:ring-green-500/50 transition-all backdrop-blur-sm"
          />
          <p className="text-xs text-neutral-500 mt-1.5 ml-1">Start from a specific URL instead of searching the web</p>
        </label>
      </div>

      {error && (
        <div className="rounded-lg bg-red-900/20 border border-red-800 p-3 flex items-start gap-2" role="alert">
          <svg className="w-4 h-4 text-red-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-red-300 text-sm">{error}</p>
        </div>
      )}

      <div className="flex gap-3">
        <button
          data-testid="submit-button"
          type="submit"
          disabled={submitting}
          className="flex-1 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-3 font-semibold shadow-lg shadow-blue-900/50 disabled:opacity-50 disabled:cursor-not-allowed hover:from-blue-700 hover:to-purple-700 transition-all duration-200 flex items-center justify-center gap-2"
        >
          {submitting ? (
            <>
              <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Submitting…</span>
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
              <span>Submit Research Task</span>
            </>
          )}
        </button>
        <button
          data-testid="clear-button"
          type="button"
          onClick={resetForm}
          className="rounded-lg border border-neutral-700 px-6 py-3 font-semibold hover:bg-neutral-800 transition-all duration-200 flex items-center justify-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          <span>Clear</span>
        </button>
      </div>
    </form>
  );
}
