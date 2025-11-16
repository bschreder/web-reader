/**
 * Accessibility tests for focus management and keyboard navigation.
 */

import { expect, test } from 'vitest'
import { page, userEvent } from 'vitest/browser'
import { render } from 'vitest-browser-react'
import { Button } from '~/components/ui/Button'
import { Input } from '~/components/ui/Input'

test('Button receives focus and can be activated with keyboard', async () => {
  let clicked = false
  render(
    <Button variant="primary" onClick={() => { clicked = true }}>
      Click Me
    </Button>
  )
  
  // Tab to focus
  await userEvent.tab()
  // Verify focused by checking active element
  await expect.poll(() => document.activeElement?.textContent).toBe('Click Me')
  
  // Activate with Space
  await userEvent.keyboard(' ')
  expect(clicked).toBe(true)
})

test('Input receives focus and accepts keyboard input', async () => {
  render(
    <Input label="Username" placeholder="Enter username" />
  )

  const input = page.getByLabelText(/Username/)
  
  // Tab to focus
  await userEvent.tab()
  await expect.poll(() => document.activeElement?.getAttribute('placeholder')).toBe('Enter username')
  
  // Type text
  await userEvent.keyboard('testuser')
  await expect.element(input).toHaveValue('testuser')
})

test('Disabled button does not receive focus', async () => {
  render(
    <div>
      <Button variant="primary" disabled>Disabled</Button>
      <Button variant="secondary">Enabled</Button>
    </div>
  )

  // Tab should skip disabled and focus enabled
  await userEvent.tab()
  await expect.poll(() => document.activeElement?.textContent).toBe('Enabled')
})

test('Input with error maintains focus and aria-invalid', async () => {
  render(
    <Input
      label="Email"
      type="email"
      error="Invalid email format"
      required
    />
  )

  const input = page.getByLabelText(/Email/)
  
  await userEvent.tab()
  await expect.poll(() => document.activeElement?.getAttribute('type')).toBe('email')
  await expect.element(input).toHaveAttribute('aria-invalid', 'true')
  
  // Error message should be associated
  const errorMsg = page.getByText(/Invalid email format/)
  await expect.element(errorMsg).toBeVisible()
  await expect.element(errorMsg).toHaveAttribute('role', 'alert')
})
