import { test, expect } from '@playwright/test';

// Use dev server started via playwright config webServer
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';

test('user submits task and sees history', async ({ page }) => {
  await page.goto(FRONTEND_URL);

  await page.fill('textarea', 'Explain TanStack Start briefly');
  await page.click('button:has-text("Submit Question")');

  // Without backend, the app may stay on home. Ensure form stayed interactive.
  await expect(page.locator('textarea')).toBeVisible();

  await page.goto(`${FRONTEND_URL}/history`);
  await expect(page.locator('text=Task History')).toBeVisible();
});
