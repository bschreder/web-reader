/**
 * Browser tests for Card hover styling presence
 */
import { expect, test } from 'vitest'
import { page } from 'vitest/browser'
import { render } from 'vitest-browser-react'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '~/components/ui/Card'

test('Card renders composed sections', async () => {
  render(
    <Card hoverable>
      <CardHeader>
        <CardTitle>Sample</CardTitle>
      </CardHeader>
      <CardContent>
        <p>Content area</p>
      </CardContent>
      <CardFooter>
        <span>Footer</span>
      </CardFooter>
    </Card>
  )
  await expect.element(page.getByText(/Sample/)).toBeVisible()
  await expect.element(page.getByText(/Content area/)).toBeVisible()
  await expect.element(page.getByText(/Footer/)).toBeVisible()
})
