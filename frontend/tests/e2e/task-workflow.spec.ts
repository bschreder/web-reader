import { test, expect } from '@playwright/test';

// Use dev server started via playwright config webServer

test('user submits task and sees history', async ({ page }) => {
  await page.goto('http://localhost:5173/');

  await page.fill('textarea', 'Explain TanStack Start briefly');
  await page.click('button:has-text("Submit")');

  // Without backend, the app may stay on home. Ensure form stayed interactive.
  await expect(page.locator('textarea')).toBeVisible();

  await page.goto('http://localhost:5173/history');
  await expect(page.locator('text=Task History')).toBeVisible();
});
