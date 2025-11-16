import { expect, test } from 'vitest'
import { page } from 'vitest/browser'
import { render } from 'vitest-browser-react'
import { TaskForm } from '~/components/TaskForm'

// Minimal stub for onSubmit to avoid network usage
function noopSubmit() {
  return Promise.resolve()
}

test('TaskForm enables submit when question is long enough', async () => {
  render(<TaskForm onSubmit={noopSubmit} submitting={false} />)

  const submitBtn = page.getByRole('button', { name: /start research/i })
  await expect.element(submitBtn).toBeDisabled()

  const textarea = page.getByLabelText(/research question/i)
  await textarea.fill('Short')
  await expect.element(submitBtn).toBeDisabled()

  await textarea.fill('What is quantum computing?')
  await expect.element(submitBtn).toBeEnabled()
})
