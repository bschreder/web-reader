/**
 * Task creation form with validation and accessibility support.
 */

import { useState } from 'react'
import type { TaskCreate } from '~/lib/types'
import { Button, Input, Card, CardContent, Alert } from '~/components/ui'

export interface TaskFormProps {
  /** Callback when form is submitted */
  onSubmit: (data: TaskCreate) => Promise<void> | void
  /** Loading state when task is being created */
  submitting?: boolean
}

/**
 * Form component for creating new research tasks.
 * 
 * @example
 * ```tsx
 * <TaskForm
 *   onSubmit={handleCreateTask}
 *   submitting={isLoading}
 * />
 * ```
 */
export function TaskForm({ onSubmit, submitting }: TaskFormProps) {
  const [question, setQuestion] = useState('')
  const [seedUrl, setSeedUrl] = useState('')
  const [maxPages, setMaxPages] = useState(10)
  const [timeBudget, setTimeBudget] = useState(60)
  const [error, setError] = useState<string>('')
  
  // Validation
  const questionError = question.length > 0 && question.trim().length < 6
    ? 'Question must be at least 6 characters'
    : ''
  
  const urlError = seedUrl.length > 0 && !isValidOrNormalizableUrl(seedUrl)
    ? 'Please enter a valid URL (http:// or https://)'
    : ''
  
  const canSubmit = question.trim().length >= 6 && !submitting && (seedUrl.length === 0 || isValidOrNormalizableUrl(seedUrl))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!canSubmit) {
      setError('Please fix form errors before submitting')
      return
    }
    
    setError('')
    
    try {
      const normalizedSeed = normalizeUrl(seedUrl)
      await onSubmit({
        question: question.trim(),
        seed_url: normalizedSeed || undefined,
        max_pages: maxPages,
        time_budget: timeBudget,
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task')
    }
  }
  
  const handleReset = () => {
    setQuestion('')
    setSeedUrl('')
    setMaxPages(10)
    setTimeBudget(60)
    setError('')
  }

  return (
    <Card>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4" data-testid="task-form">
          {error && (
            <Alert variant="danger" onClose={() => setError('')}>
              {error}
            </Alert>
          )}
          
          <div>
            <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-2">
              Research Question
              <span className="text-red-500 ml-1" aria-label="required">*</span>
            </label>
            <textarea
              id="question"
              className="block w-full rounded-md border border-gray-300 shadow-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              rows={3}
              placeholder="What would you like to research? Be specific for better results."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              data-testid="question"
              aria-invalid={Boolean(questionError)}
              aria-describedby={questionError ? "question-error" : "question-helper"}
              required
            />
            {questionError ? (
              <p id="question-error" className="mt-1 text-sm text-red-600" role="alert">
                {questionError}
              </p>
            ) : (
              <p id="question-helper" className="mt-1 text-sm text-gray-500">
                Ask a specific question to get better results. Min 6 characters.
              </p>
            )}
          </div>
          
          <Input
            label="Seed URL (Optional)"
            type="url"
            placeholder="https://example.com"
            value={seedUrl}
            onChange={(e) => setSeedUrl(e.target.value)}
            error={urlError}
            helperText="Starting point for research. Agent will search if not provided."
          />
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Max Pages"
              type="number"
              min={1}
              max={50}
              value={maxPages.toString()}
              onChange={(e) => setMaxPages(parseInt(e.target.value) || 1)}
              helperText="Maximum number of pages to visit (1-50)"
              required
            />
            
            <Input
              label="Time Budget (seconds)"
              type="number"
              min={10}
              max={300}
              value={timeBudget.toString()}
              onChange={(e) => setTimeBudget(parseInt(e.target.value) || 10)}
              helperText="Maximum time for research (10-300s)"
              required
            />
          </div>
          
          <div className="flex gap-3 pt-2">
            <Button
              type="submit"
              variant="primary"
              size="md"
              isLoading={submitting}
              disabled={!canSubmit}
            >
              {submitting ? 'Starting Task...' : 'Start Research'}
            </Button>
            
            <Button
              type="button"
              variant="secondary"
              size="md"
              onClick={handleReset}
              disabled={submitting}
            >
              Reset Form
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}

/**
 * Validate URL format.
 * @param url - URL string to validate
 * @returns true if valid URL
 */
function isValidOrNormalizableUrl(input: string): boolean {
  if (!input) return true
  if (isAbsoluteHttpUrl(input)) return true
  // Allow domain-only inputs like example.com by implicitly prefixing https://
  if (looksLikeDomain(input)) {
    return isAbsoluteHttpUrl(`https://${input}`)
  }
  return false
}

function normalizeUrl(input: string): string | '' {
  if (!input) return ''
  if (isAbsoluteHttpUrl(input)) return input
  if (looksLikeDomain(input)) {
    const candidate = `https://${input}`
    return isAbsoluteHttpUrl(candidate) ? candidate : ''
  }
  return ''
}

function isAbsoluteHttpUrl(url: string): boolean {
  try {
    const parsed = new URL(url)
    return parsed.protocol === 'http:' || parsed.protocol === 'https:'
  } catch {
    return false
  }
}

function looksLikeDomain(value: string): boolean {
  // Basic heuristic: contains a dot, no spaces, not starting with a scheme
  // This avoids accepting strings like 'not-a-valid-url'
  const v = value.trim()
  if (!v || /\s/.test(v)) return false
  if (/^https?:\/\//i.test(v)) return false
  // require at least one dot and a TLD-like segment (2+ letters)
  const parts = v.split('.')
  if (parts.length < 2) return false
  const tld = parts[parts.length - 1] ?? ''
  return /^[a-zA-Z]{2,}$/.test(tld)
}

export default TaskForm
