import { test, expect } from 'vitest'
import { page } from 'vitest/browser'
import { render } from 'vitest-browser-react'
import { Button } from '~/components/ui/Button'

// Basic interactive test without testing-library

test('Button is disabled when loading', async () => {
  render(<Button variant="primary" isLoading>Do Work</Button>)
  const btn = page.getByRole('button', { name: /do work/i })
  await expect.element(btn).toBeInTheDocument()
  await expect.element(btn).toBeDisabled()
})

test('Button disabled state propagates', async () => {
  render(<Button variant="secondary" disabled>Disabled</Button>)
  const btn = page.getByRole('button', { name: /disabled/i })
  await expect.element(btn).toBeDisabled()
})
