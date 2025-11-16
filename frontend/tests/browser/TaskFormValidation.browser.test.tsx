/**
 * Browser tests for TaskForm validation edge cases.
 */

import { expect, test } from 'vitest'
import { page } from 'vitest/browser'
import { render } from 'vitest-browser-react'
import { TaskForm } from '~/components/TaskForm'

test('TaskForm shows error for short question', async () => {
  render(<TaskForm onSubmit={() => Promise.resolve()} submitting={false} />)

  const textarea = page.getByTestId('question')
  await textarea.fill('Hi')
  
  // Error should appear after typing < 6 chars
  const errorMsg = page.getByText(/Question must be at least 6 characters/)
  await expect.element(errorMsg).toBeVisible()
  
  // Submit should be disabled
  const submitBtn = page.getByRole('button', { name: /Start Research/ })
  await expect.element(submitBtn).toBeDisabled()
})

test('TaskForm shows error for invalid URL', async () => {
  render(<TaskForm onSubmit={() => Promise.resolve()} submitting={false} />)

  // Fill valid question first
  const textarea = page.getByTestId('question')
  await textarea.fill('What is quantum computing?')
  
  // Fill invalid URL
  const urlInput = page.getByLabelText(/Seed URL/)
  await urlInput.fill('not-a-valid-url')
  
  // URL error should appear
  const urlError = page.getByText(/Please enter a valid URL/)
  await expect.element(urlError).toBeVisible()
  
  // Submit should be disabled
  const submitBtn = page.getByRole('button', { name: /Start Research/ })
  await expect.element(submitBtn).toBeDisabled()
})

test('TaskForm reset clears all fields', async () => {
  render(<TaskForm onSubmit={() => Promise.resolve()} submitting={false} />)

  // Fill out form
  const textarea = page.getByTestId('question')
  await textarea.fill('What is quantum computing?')
  
  const urlInput = page.getByLabelText(/Seed URL/)
  await urlInput.fill('https://example.com')
  
  // Click reset
  const resetBtn = page.getByRole('button', { name: /Reset Form/ })
  await resetBtn.click()
  
  // Fields should be cleared
  await expect.element(textarea).toHaveValue('')
  await expect.element(urlInput).toHaveValue('')
})

test('TaskForm accepts valid http and https URLs', async () => {
  render(<TaskForm onSubmit={() => Promise.resolve()} submitting={false} />)

  const textarea = page.getByTestId('question')
  await textarea.fill('What is quantum computing?')
  
  const urlInput = page.getByLabelText(/Seed URL/)
  
  // Test https
  await urlInput.fill('https://example.com')
  const submitBtn = page.getByRole('button', { name: /Start Research/ })
  await expect.element(submitBtn).toBeEnabled()
  
  // Test http
  await urlInput.fill('http://example.com')
  await expect.element(submitBtn).toBeEnabled()
})
