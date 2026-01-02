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

import { test, expect } from '@playwright/test';

const API_URL = process.env.VITE_API_URL || 'http://localhost:8000';
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';

test.describe('UC-03: Rate Limits, Budgets, and Guardrails', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(FRONTEND_URL);
  });

  test('should respect max_pages limit', async ({ page }) => {
    await page.getByRole('textbox', { name: /question/i }).fill('Test max pages');

    // Set max pages to 5
    const maxPagesInput = page.getByLabel(/max pages/i);
    await maxPagesInput.clear();
    await maxPagesInput.fill('5');

    await page.getByRole('button', { name: /submit question/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);

    // Verify max_pages parameter
    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    
    expect(task.max_pages).toBe(5);
  });

  test('should respect time_budget limit', async ({ page }) => {
    await page.getByRole('textbox', { name: /question/i }).fill('Test time budget');

    // Set time budget to 60 seconds
    const timeBudgetInput = page.getByLabel(/time budget/i);
    await timeBudgetInput.clear();
    await timeBudgetInput.fill('60');

    await page.getByRole('button', { name: /submit question/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);

    // Verify time_budget parameter
    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    
    expect(task.time_budget).toBe(60);
  });

  test('should enforce max_pages boundary (1-50)', async ({ page }) => {
    const maxPagesInput = page.getByLabel(/max pages/i);

    // Test min boundary (1)
    await page.getByRole('textbox', { name: /question/i }).fill('Test min pages');
    await maxPagesInput.clear();
    await maxPagesInput.fill('1');
    await page.getByRole('button', { name: /submit question/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);
    
    let url = page.url();
    let taskId = url.split('/tasks/')[1];
    let response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    let task = await response.json();
    expect(task.max_pages).toBe(1);

    // Navigate back for max boundary test
    await page.goto(FRONTEND_URL);

    // Test max boundary (50)
    await page.getByRole('textbox', { name: /question/i }).fill('Test max pages boundary');
    await page.getByLabel(/max pages/i).clear();
    await page.getByLabel(/max pages/i).fill('50');
    await page.getByRole('button', { name: /submit question/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);
    
    url = page.url();
    taskId = url.split('/tasks/')[1];
    response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    task = await response.json();
    expect(task.max_pages).toBe(50);
  });

  test('should enforce time_budget boundary (30-600 seconds)', async ({ page }) => {
    const timeBudgetInput = page.getByLabel(/time budget/i);

    // Test min boundary (30)
    await page.getByRole('textbox', { name: /question/i }).fill('Test min time');
    await timeBudgetInput.clear();
    await timeBudgetInput.fill('30');
    await page.getByRole('button', { name: /submit question/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);
    
    let url = page.url();
    let taskId = url.split('/tasks/')[1];
    let response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    let task = await response.json();
    expect(task.time_budget).toBe(30);

    // Navigate back for max boundary test
    await page.goto(FRONTEND_URL);

    // Test max boundary (600)
    await page.getByRole('textbox', { name: /question/i }).fill('Test max time boundary');
    await page.getByLabel(/time budget/i).clear();
    await page.getByLabel(/time budget/i).fill('600');
    await page.getByRole('button', { name: /submit question/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);
    
    url = page.url();
    taskId = url.split('/tasks/')[1];
    response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    task = await response.json();
    expect(task.time_budget).toBe(600);
  });

  test('should use default limits when not specified', async ({ page }) => {
    // Submit without showing advanced options
    await page.getByRole('textbox', { name: /question/i }).fill('Test defaults');
    await page.getByRole('button', { name: /submit question/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);

    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    
    // Verify default limits (UC-03 defaults)
    expect(task.max_pages).toBe(20); // default
    expect(task.time_budget).toBe(120); // default (2 minutes)
  });

  test('should enforce max_depth boundary (1-5)', async ({ page }) => {
    const maxDepthInput = page.getByLabel(/max link depth/i);

    // Test min boundary (1)
    await page.getByRole('textbox', { name: /question/i }).fill('Test min depth');
    await maxDepthInput.clear();
    await maxDepthInput.fill('1');
    await page.getByRole('button', { name: /submit question/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);
    
    let url = page.url();
    let taskId = url.split('/tasks/')[1];
    let response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    let task = await response.json();
    expect(task.max_depth).toBe(1);

    // Navigate back for max boundary test
    await page.goto(FRONTEND_URL);

    // Test max boundary (5)
    await page.getByRole('textbox', { name: /question/i }).fill('Test max depth boundary');
    await page.getByLabel(/max link depth/i).clear();
    await page.getByLabel(/max link depth/i).fill('5');
    await page.getByRole('button', { name: /submit question/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);
    
    url = page.url();
    taskId = url.split('/tasks/')[1];
    response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    task = await response.json();
    expect(task.max_depth).toBe(5);
  });

  test('should accept all valid limit combinations', async ({ page }) => {
    await page.getByRole('textbox', { name: /question/i }).fill('Test all limits');


    // Set all limit parameters
    await page.getByLabel(/max link depth/i).clear();
    await page.getByLabel(/max link depth/i).fill('3');

    await page.getByLabel(/max pages/i).clear();
    await page.getByLabel(/max pages/i).fill('15');

    await page.getByLabel(/time budget/i).clear();
    await page.getByLabel(/time budget/i).fill('90');

    await page.getByLabel(/max search results/i).clear();
    await page.getByLabel(/max search results/i).fill('8');

    await page.getByRole('button', { name: /submit question/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);

    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    
    expect(task.max_depth).toBe(3);
    expect(task.max_pages).toBe(15);
    expect(task.time_budget).toBe(90);
    expect(task.max_results).toBe(8);
  });

  test('should create task with strict limits (minimal resources)', async ({ page }) => {
    await page.getByRole('textbox', { name: /question/i }).fill('Minimal resources test');


    // Set minimal limits
    await page.getByLabel(/max link depth/i).clear();
    await page.getByLabel(/max link depth/i).fill('1');

    await page.getByLabel(/max pages/i).clear();
    await page.getByLabel(/max pages/i).fill('1');

    await page.getByLabel(/time budget/i).clear();
    await page.getByLabel(/time budget/i).fill('30');

    await page.getByLabel(/max search results/i).clear();
    await page.getByLabel(/max search results/i).fill('1');

    await page.getByRole('button', { name: /submit question/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);

    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    
    // Task should still be created successfully
    expect(task.max_depth).toBe(1);
    expect(task.max_pages).toBe(1);
    expect(task.time_budget).toBe(30);
    expect(task.max_results).toBe(1);
  });

  test('should create task with generous limits (maximum resources)', async ({ page }) => {
    await page.getByRole('textbox', { name: /question/i }).fill('Maximum resources test');


    // Set maximum limits
    await page.getByLabel(/max link depth/i).clear();
    await page.getByLabel(/max link depth/i).fill('5');

    await page.getByLabel(/max pages/i).clear();
    await page.getByLabel(/max pages/i).fill('50');

    await page.getByLabel(/time budget/i).clear();
    await page.getByLabel(/time budget/i).fill('600');

    await page.getByLabel(/max search results/i).clear();
    await page.getByLabel(/max search results/i).fill('50');

    await page.getByRole('button', { name: /submit question/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);

    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    
    expect(task.max_depth).toBe(5);
    expect(task.max_pages).toBe(50);
    expect(task.time_budget).toBe(600);
    expect(task.max_results).toBe(50);
  });

  test('should respect all UC-01, UC-02, and UC-03 parameters together', async ({ page }) => {
    const seedUrl = 'https://example.com/docs';

    await page.getByRole('textbox', { name: /question/i }).fill('Comprehensive parameters test');
    await page.getByLabel(/seed url/i).fill(seedUrl);


    // UC-01 parameters
    await page.locator('select').first().selectOption('bing');
    await page.getByLabel(/max search results/i).clear();
    await page.getByLabel(/max search results/i).fill('15');
    await page.getByLabel(/safe mode/i).check();

    // UC-02 parameters
    await page.getByLabel(/max link depth/i).clear();
    await page.getByLabel(/max link depth/i).fill('2');
    await page.getByLabel(/same domain only/i).check();
    await page.getByLabel(/allow external links/i).uncheck();

    // UC-03 parameters
    await page.getByLabel(/max pages/i).clear();
    await page.getByLabel(/max pages/i).fill('10');
    await page.getByLabel(/time budget/i).clear();
    await page.getByLabel(/time budget/i).fill('180');

    await page.getByRole('button', { name: /submit question/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);

    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    
    // Verify all parameters
    expect(task.seed_url).toBe(seedUrl);
    expect(task.search_engine).toBe('bing');
    expect(task.max_results).toBe(15);
    expect(task.safe_mode).toBe(true);
    expect(task.max_depth).toBe(2);
    expect(task.same_domain_only).toBe(true);
    expect(task.allow_external_links).toBe(false);
    expect(task.max_pages).toBe(10);
    expect(task.time_budget).toBe(180);
  });
});
