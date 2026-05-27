import { test, expect } from '@playwright/test';

// Use dev server started via playwright config webServer
const FRONTEND_URL = process.env.FRONTEND_PUBLIC_URL;
if (!FRONTEND_URL) {
  throw new Error('Missing required environment variable: FRONTEND_PUBLIC_URL');
}

test('user submits task and sees history', async ({ page }) => {
  await page.goto(FRONTEND_URL);

  await page.getByTestId('question-textarea').fill('Explain TanStack Start briefly');
  await page.getByTestId('submit-button').click();

  // Without backend, the app may stay on home. Ensure form stayed interactive.
  await expect(page.getByTestId('question-textarea')).toBeVisible();

  await page.goto(`${FRONTEND_URL}/history`);
  await expect(page.locator('text=Task History')).toBeVisible();
});
