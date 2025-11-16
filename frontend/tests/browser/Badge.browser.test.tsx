/**
 * Browser tests for Badge component.
 */

import { expect, test } from 'vitest'
import { page } from 'vitest/browser'
import { render } from 'vitest-browser-react'
import { Badge } from '~/components/ui/Badge'

test('Badge renders with correct variant styles', async () => {
  render(
    <div>
      <Badge variant="success" data-testid="success-badge">
        Completed
      </Badge>
      <Badge variant="danger" data-testid="danger-badge">
        Failed
      </Badge>
    </div>
  )
  
  const successBadge = page.getByTestId('success-badge')
  await expect.element(successBadge).toBeVisible()
  await expect.element(successBadge).toHaveTextContent('Completed')
  
  const dangerBadge = page.getByTestId('danger-badge')
  await expect.element(dangerBadge).toBeVisible()
  await expect.element(dangerBadge).toHaveTextContent('Failed')
})
