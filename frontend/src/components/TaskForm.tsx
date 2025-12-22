import React, { JSX, useState } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { createTask } from '@lib/api';

/**
 * TaskForm collects question and optional seed URL then creates a task.
 * @returns {JSX.Element} The task form component
 */
export default function TaskForm(): JSX.Element {
  const navigate = useNavigate();
  const [question, setQuestion] = useState('');
  const [seedUrl, setSeedUrl] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
      const { id } = await createTask({ question, seedUrl: seedUrl || undefined });
      navigate({ to: '/tasks/$id', params: { id } });
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <label className="block">
        <span className="text-sm">Question</span>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          className="mt-1 w-full rounded border border-neutral-700 bg-neutral-900 p-2"
          rows={4}
          required
        />
      </label>
      <label className="block">
        <span className="text-sm">Seed URL (optional)</span>
        <input
          value={seedUrl}
          onChange={(e) => setSeedUrl(e.target.value)}
          type="url"
          placeholder="https://example.com"
          className="mt-1 w-full rounded border border-neutral-700 bg-neutral-900 p-2"
        />
      </label>
      {error && <p className="text-red-400" role="alert">{error}</p>}
      <button
        type="submit"
        disabled={submitting}
        className="rounded bg-blue-600 px-4 py-2 font-semibold disabled:opacity-50"
      >
        {submitting ? 'Submitting…' : 'Submit Task'}
      </button>
    </form>
  );
}
