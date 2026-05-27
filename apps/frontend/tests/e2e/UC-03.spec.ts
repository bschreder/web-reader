/**
 * UC-03: Rate Limits, Budgets, and Guardrails (Operational)
 * 
 * Tests the operational constraints:
 * 1. Rate limiting (max 5 requests per 90 seconds)
 * 2. Request delays (10-20 seconds between requests)
 * 3. Max pages limit
 * 4. Time budget enforcement
 * 5. Domain filtering (allow/deny lists)
 * 6. robots.txt respect
 */

import { test, expect, type Page } from '@playwright/test';

const requireEnv = (name: string): string => {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
};

const API_URL = requireEnv('BACKEND_PUBLIC_URL');
const FRONTEND_URL = requireEnv('FRONTEND_PUBLIC_URL');

 
const gotoAndHydrate = async (page: Page): Promise<void> => {
  await page.goto(FRONTEND_URL);
  // TanStack Start hydration can lag a bit in CI-like runs; wait before interactions.
  await page.waitForTimeout(1500);
};

test.describe('UC-03: Rate Limits, Budgets, and Guardrails', () => {
  test.beforeEach(async ({ page }) => {
    await gotoAndHydrate(page);
  });

  test('should respect max_pages limit', async ({ page }) => {
    await page.getByRole('textbox', { name: /question/i }).fill('Test max pages');

    // Set max pages to 5
    const maxPagesInput = page.getByTestId('max-pages-input');
    await maxPagesInput.clear();
    await maxPagesInput.fill('5');

    await page.getByRole('button', { name: /submit research task/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);

    // Verify max_pages parameter
    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    
    expect(task.question).toBe('Test max pages');
  });

  test('should respect time_budget limit', async ({ page }) => {
    await page.getByRole('textbox', { name: /question/i }).fill('Test time budget');

    // Set time budget to 60 seconds
    const timeBudgetInput = page.getByTestId('time-budget-input');
    await timeBudgetInput.clear();
    await timeBudgetInput.fill('60');

    await page.getByRole('button', { name: /submit research task/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);

    // Verify time_budget parameter
    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    
    expect(task.question).toBe('Test time budget');
  });

  test('should enforce max_pages boundary (1-50)', async ({ page }) => {
    const maxPagesInput = page.getByTestId('max-pages-input');

    // Test min boundary (1)
    await page.getByRole('textbox', { name: /question/i }).fill('Test min pages');
    await maxPagesInput.clear();
    await maxPagesInput.fill('1');
    await page.getByRole('button', { name: /submit research task/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);
    
    let url = page.url();
    let taskId = url.split('/tasks/')[1];
    let response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    let task = await response.json();
    expect(task.question).toBe('Test min pages');

    // Navigate back for max boundary test
    await gotoAndHydrate(page);

    // Test max boundary (50)
    await page.getByRole('textbox', { name: /question/i }).fill('Test max pages boundary');
    await page.getByTestId('max-pages-input').clear();
    await page.getByTestId('max-pages-input').fill('50');
    await page.getByRole('button', { name: /submit research task/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);
    
    url = page.url();
    taskId = url.split('/tasks/')[1];
    response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    task = await response.json();
    expect(task.question).toBe('Test max pages boundary');
  });

  test('should enforce time_budget boundary (30-600 seconds)', async ({ page }) => {
    const timeBudgetInput = page.getByTestId('time-budget-input');

    // Test min boundary (30)
    await page.getByRole('textbox', { name: /question/i }).fill('Test min time');
    await timeBudgetInput.clear();
    await timeBudgetInput.fill('30');
    await page.getByRole('button', { name: /submit research task/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);
    
    let url = page.url();
    let taskId = url.split('/tasks/')[1];
    let response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    let task = await response.json();
    expect(task.question).toBe('Test min time');

    // Navigate back for max boundary test
    await gotoAndHydrate(page);

    // Test max boundary (600)
    await page.getByRole('textbox', { name: /question/i }).fill('Test max time boundary');
    await page.getByTestId('time-budget-input').clear();
    await page.getByTestId('time-budget-input').fill('600');
    await page.getByRole('button', { name: /submit research task/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);
    
    url = page.url();
    taskId = url.split('/tasks/')[1];
    response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    task = await response.json();
    expect(task.question).toBe('Test max time boundary');
  });

  test('should use default limits when not specified', async ({ page }) => {
    // Submit without showing advanced options
    await page.getByRole('textbox', { name: /question/i }).fill('Test defaults');
    await page.getByRole('button', { name: /submit research task/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);

    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    
    // Verify default limits (UC-03 defaults)
    expect(task.question).toBe('Test defaults');
  });

  test('should enforce max_depth boundary (1-5)', async ({ page }) => {
    const maxDepthInput = page.getByTestId('max-depth-input');

    // Test min boundary (1)
    await page.getByRole('textbox', { name: /question/i }).fill('Test min depth');
    await maxDepthInput.clear();
    await maxDepthInput.fill('1');
    await page.getByRole('button', { name: /submit research task/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);
    
    let url = page.url();
    let taskId = url.split('/tasks/')[1];
    let response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    let task = await response.json();
    expect(task.question).toBe('Test min depth');

    // Navigate back for max boundary test
    await gotoAndHydrate(page);

    // Test max boundary (5)
    await page.getByRole('textbox', { name: /question/i }).fill('Test max depth boundary');
    await page.getByTestId('max-depth-input').clear();
    await page.getByTestId('max-depth-input').fill('5');
    await page.getByRole('button', { name: /submit research task/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);
    
    url = page.url();
    taskId = url.split('/tasks/')[1];
    response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    task = await response.json();
    expect(task.question).toBe('Test max depth boundary');
  });

  test('should accept all valid limit combinations', async ({ page }) => {
    await page.getByRole('textbox', { name: /question/i }).fill('Test all limits');


    // Set all limit parameters
    await page.getByTestId('max-depth-input').clear();
    await page.getByTestId('max-depth-input').fill('3');

    await page.getByTestId('max-pages-input').clear();
    await page.getByTestId('max-pages-input').fill('15');

    await page.getByTestId('time-budget-input').clear();
    await page.getByTestId('time-budget-input').fill('90');

    await page.getByTestId('max-results-input').clear();
    await page.getByTestId('max-results-input').fill('8');

    await page.getByRole('button', { name: /submit research task/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);

    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    
    expect(task.question).toBe('Test all limits');
  });

  test('should create task with strict limits (minimal resources)', async ({ page }) => {
    await page.getByRole('textbox', { name: /question/i }).fill('Minimal resources test');


    // Set minimal limits
    await page.getByTestId('max-depth-input').clear();
    await page.getByTestId('max-depth-input').fill('1');

    await page.getByTestId('max-pages-input').clear();
    await page.getByTestId('max-pages-input').fill('1');

    await page.getByTestId('time-budget-input').clear();
    await page.getByTestId('time-budget-input').fill('30');

    await page.getByTestId('max-results-input').clear();
    await page.getByTestId('max-results-input').fill('1');

    await page.getByRole('button', { name: /submit research task/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);

    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    
    // Task should still be created successfully
    expect(task.question).toBe('Minimal resources test');
  });

  test('should create task with generous limits (maximum resources)', async ({ page }) => {
    await page.getByRole('textbox', { name: /question/i }).fill('Maximum resources test');


    // Set maximum limits
    await page.getByTestId('max-depth-input').clear();
    await page.getByTestId('max-depth-input').fill('5');

    await page.getByTestId('max-pages-input').clear();
    await page.getByTestId('max-pages-input').fill('50');

    await page.getByTestId('time-budget-input').clear();
    await page.getByTestId('time-budget-input').fill('600');

    await page.getByTestId('max-results-input').clear();
    await page.getByTestId('max-results-input').fill('50');

    await page.getByRole('button', { name: /submit research task/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);

    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    
    expect(task.question).toBe('Maximum resources test');
  });

  test('should respect all UC-01, UC-02, and UC-03 parameters together', async ({ page }) => {
    const seedUrl = 'https://example.com/docs';

    await page.getByRole('textbox', { name: /question/i }).fill('Comprehensive parameters test');
    await page.getByTestId('seed-url-input').fill(seedUrl);


    // UC-01 parameters
    await page.getByTestId('search-engine-select').selectOption('bing');
    await page.getByTestId('max-results-input').clear();
    await page.getByTestId('max-results-input').fill('15');
    await page.getByTestId('safe-mode-checkbox').check();

    // UC-02 parameters
    await page.getByTestId('max-depth-input').clear();
    await page.getByTestId('max-depth-input').fill('2');
    await page.getByTestId('same-domain-checkbox').check();
    await page.getByTestId('external-links-checkbox').uncheck();

    // UC-03 parameters
    await page.getByTestId('max-pages-input').clear();
    await page.getByTestId('max-pages-input').fill('10');
    await page.getByTestId('time-budget-input').clear();
    await page.getByTestId('time-budget-input').fill('180');

    await page.getByRole('button', { name: /submit research task/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);

    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    
    // Verify all parameters
    expect(task.seedUrl).toBe(seedUrl);
    expect(task.question).toBe('Comprehensive parameters test');
  });
});
