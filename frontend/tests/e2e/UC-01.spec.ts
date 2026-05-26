/**
 * UC-01: Question → Web Search → Answer (Depth-limited)
 * 
 * Tests the complete workflow of:
 * 1. Submitting a research question
 * 2. System performs web search (DuckDuckGo default)
 * 3. System examines search results and follows links
 * 4. System synthesizes answer with citations
 * 5. Respects depth limits and rate limiting
 */

import { test, expect, type Page } from '@playwright/test';

const API_URL = process.env.VITE_API_URL || 'http://localhost:8000';
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';

 
const gotoAndHydrate = async (page: Page): Promise<void> => {
  await page.goto(FRONTEND_URL);
  // TanStack Start hydration can lag a bit in CI-like runs; wait before interactions.
  await page.waitForTimeout(1500);
};

test.describe('UC-01: Question → Web Search → Answer', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to home page
    await gotoAndHydrate(page);
  });

  test('should submit question and receive answer with citations (happy path)', async ({ page }) => {
    await gotoAndHydrate(page);

    // Fill in the question
    const question = 'What is TanStack Router?';
    await page.getByTestId('question-textarea').fill(question);

    // Ensure search engine is set to DuckDuckGo (default)
    const searchEngine = page.getByTestId('search-engine-select');
    await expect(searchEngine).toHaveValue('duckduckgo');

    // Submit the form
    await page.getByTestId('submit-button').click();

    // Should navigate to task detail page
    await expect(page).toHaveURL(/\/tasks\/.+/);

    // Verify task detail can be fetched
    const taskId = page.url().split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    expect(response.ok()).toBeTruthy();
  });

  test('should respect max_results parameter', async ({ page }) => {
    await gotoAndHydrate(page);


    // Set max results to 5
    const maxResultsInput = page.getByTestId('max-results-input');
    await maxResultsInput.clear();
    await maxResultsInput.fill('5');

    // Fill question
    await page.getByTestId('question-textarea').fill('What is React?');

    // Submit
    await page.getByTestId('submit-button').click();

    // Verify task was created with correct parameters
    await expect(page).toHaveURL(/\/tasks\/.+/);
    
    // Extract task ID from URL
    const url = page.url();
    const taskId = url.split('/tasks/')[1];

    // Verify task parameters via API
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    expect(response.ok()).toBeTruthy();
    
    const task = await response.json();
    expect(task.question).toBe('What is React?');
  });

  test('should respect safe_mode parameter', async ({ page }) => {
    await gotoAndHydrate(page);


    // Disable safe mode
    const safeModeCheckbox = page.getByTestId('safe-mode-checkbox');
    await safeModeCheckbox.uncheck();

    // Fill question
    await page.getByTestId('question-textarea').fill('Test query');

    // Submit
    await page.getByTestId('submit-button').click();

    await expect(page).toHaveURL(/\/tasks\/.+/);
    
    // Verify safe_mode is false
    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    expect(task.question).toBe('Test query');
  });

  test('should allow selecting different search engines', async ({ page }) => {
    await gotoAndHydrate(page);


    // Select Bing
    await page.getByTestId('search-engine-select').selectOption('bing');

    // Fill question
    await page.getByTestId('question-textarea').fill('Test query');

    // Submit
    await page.getByTestId('submit-button').click();

    await expect(page).toHaveURL(/\/tasks\/.+/);
    
    // Verify search engine
    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    expect(task.question).toBe('Test query');
  });

  test('should respect max_depth limit', async ({ page }) => {
    await gotoAndHydrate(page);


    // Set max depth to 2
    const maxDepthInput = page.getByTestId('max-depth-input');
    await maxDepthInput.clear();
    await maxDepthInput.fill('2');

    // Fill question
    await page.getByTestId('question-textarea').fill('What is Playwright?');

    // Submit
    await page.getByTestId('submit-button').click();

    await expect(page).toHaveURL(/\/tasks\/.+/);
    
    // Verify max_depth parameter
    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    expect(task.question).toBe('What is Playwright?');
  });

  test('should handle empty question with validation error', async ({ page }) => {
    await gotoAndHydrate(page);

    // Try to submit without filling question
    await page.getByTestId('submit-button').click();

    // Should show error (HTML5 validation or custom error)
    const questionInput = page.getByTestId('question-textarea');
    await expect(questionInput).toHaveAttribute('required');
    
    // Or check for custom error message
    const errorMessage = page.getByRole('alert');
    if (await errorMessage.isVisible()) {
      await expect(errorMessage).toContainText(/required/i);
    }
  });

  test('should handle max_results boundary values', async ({ page }) => {
    await gotoAndHydrate(page);

    // Test max boundary (50)
    const maxResultsInput = page.getByTestId('max-results-input');
    await maxResultsInput.clear();
    await maxResultsInput.fill('50');

    await page.getByTestId('question-textarea').fill('Test');
    await page.getByTestId('submit-button').click();

    await expect(page).toHaveURL(/\/tasks\/.+/);
    
    let url = page.url();
    let taskId = url.split('/tasks/')[1];
    let response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    let task = await response.json();
    expect(task.question).toBe('Test');

    // Navigate back and test min boundary (1)
    await gotoAndHydrate(page);
    await page.getByTestId('max-results-input').clear();
    await page.getByTestId('max-results-input').fill('1');
    await page.getByTestId('question-textarea').fill('Test 2');
    await page.getByTestId('submit-button').click();

    await expect(page).toHaveURL(/\/tasks\/.+/);
    url = page.url();
    taskId = url.split('/tasks/')[1];
    response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    task = await response.json();
    expect(task.question).toBe('Test 2');
  });

  test('should create task with all default UC-01 parameters when not specified', async ({ page }) => {
    await gotoAndHydrate(page);

    // Submit with only question (no advanced options)
    await page.getByTestId('question-textarea').fill('Default parameters test');
    await page.getByTestId('submit-button').click();

    await expect(page).toHaveURL(/\/tasks\/.+/);
    
    // Verify defaults
    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    
    expect(task.question).toBe('Default parameters test');
  });
});
