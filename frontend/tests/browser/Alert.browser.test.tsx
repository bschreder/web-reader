/**
 * Browser tests for Alert component interactive behavior
 */
import { expect, test } from 'vitest'
import { page } from 'vitest/browser'
import { render } from 'vitest-browser-react'
import { Alert } from '~/components/ui/Alert'

// Close handler state surrogate
let closed = false

function reset() { closed = false }

test('Alert renders title and content + can close', async () => {
  reset()
  render(
    <Alert variant="success" title="Success" onClose={() => { closed = true }}>
      Operation completed.
    </Alert>
  )
  const title = page.getByText(/Success/)
  await expect.element(title).toBeVisible()
  const content = page.getByText(/Operation completed/)
  await expect.element(content).toBeVisible()
  const closeBtn = page.getByRole('button', { name: /close alert/i })
  await expect.element(closeBtn).toBeVisible()
  await closeBtn.click()
  // Even though DOM might not auto-remove, handler state should update
  expect(closed).toBe(true)
})
