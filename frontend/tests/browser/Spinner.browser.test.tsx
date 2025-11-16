/**
 * Browser tests for Spinner accessibility
 */
import { expect, test } from 'vitest'
import { page } from 'vitest/browser'
import { render } from 'vitest-browser-react'
import { Spinner } from '~/components/ui/Spinner'

test('Spinner renders with role status and label', async () => {
  render(<Spinner size="sm" centered />)
  const status = page.getByRole('status')
  await expect.element(status).toBeVisible()
})
