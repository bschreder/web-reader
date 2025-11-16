/**
 * Additional TaskForm tests for error handling and edge cases.
 */

import { expect, test, vi } from 'vitest'
import { page } from 'vitest/browser'
import { render } from 'vitest-browser-react'
import { TaskForm } from '~/components/TaskForm'

test('TaskForm shows error when submit fails', async () => {
  const failingSubmit = vi.fn().mockRejectedValue(new Error('Network error'))
  
  render(<TaskForm onSubmit={failingSubmit} submitting={false} />)

  // Fill valid question
  const textarea = page.getByTestId('question')
  await textarea.fill('What is quantum computing?')
  
  // Submit form
  const submitBtn = page.getByRole('button', { name: /Start Research/ })
  await submitBtn.click()
  
  // Wait for error to appear
  await new Promise(resolve => setTimeout(resolve, 200))
  
  const errorMsg = page.getByText(/Network error/)
  await expect.element(errorMsg).toBeVisible()
})

test('TaskForm shows error when submitting with invalid state', async () => {
  render(<TaskForm onSubmit={() => Promise.resolve()} submitting={false} />)

  // Fill question below minimum
  const textarea = page.getByTestId('question')
  await textarea.fill('Hi')
  
  // Button should be disabled (no click needed)
  const submitBtn = page.getByRole('button', { name: /Start Research/ })
  await expect.element(submitBtn).toBeDisabled()
})

test('TaskForm handles numeric input edge cases', async () => {
  render(<TaskForm onSubmit={() => Promise.resolve()} submitting={false} />)

  const pagesInput = page.getByLabelText(/Max Pages/)
  const budgetInput = page.getByLabelText(/Time Budget/)

  // Fill with valid numbers
  await pagesInput.fill('5')
  await budgetInput.fill('30')

  // Verify values (numeric inputs return numbers)
  await expect.element(pagesInput).toHaveValue(5)
  await expect.element(budgetInput).toHaveValue(30)
})

test('TaskForm clears error when alert is closed', async () => {
  const failingSubmit = vi.fn().mockRejectedValue(new Error('API error'))
  
  render(<TaskForm onSubmit={failingSubmit} submitting={false} />)

  // Fill and submit to trigger error
  const textarea = page.getByTestId('question')
  await textarea.fill('What is quantum computing?')
  
  const submitBtn = page.getByRole('button', { name: /Start Research/ })
  await submitBtn.click()
  
  await new Promise(resolve => setTimeout(resolve, 200))
  
  // Error should be visible
  const errorMsg = page.getByText(/API error/)
  await expect.element(errorMsg).toBeVisible()
  
  // Close alert
  const closeBtn = page.getByRole('button', { name: /close alert/i })
  await closeBtn.click()
  
  // Error should be gone
  await expect.element(errorMsg).not.toBeInTheDocument()
})

test('TaskForm submits with trimmed question and optional fields', async () => {
  const submitSpy = vi.fn().mockResolvedValue(undefined)
  
  render(<TaskForm onSubmit={submitSpy} submitting={false} />)

  // Fill question with extra whitespace
  const textarea = page.getByTestId('question')
  await textarea.fill('  What is quantum computing?  ')
  
  // Leave seed URL empty
  
  const submitBtn = page.getByRole('button', { name: /Start Research/ })
  await submitBtn.click()
  
  await new Promise(resolve => setTimeout(resolve, 200))
  
  expect(submitSpy).toHaveBeenCalledWith({
    question: 'What is quantum computing?',
    seed_url: undefined,
    max_pages: 10,
    time_budget: 60,
  })
})
