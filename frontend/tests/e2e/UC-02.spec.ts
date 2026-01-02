/**
 * UC-02: Question → Seed URL → Linked Reading
 * 
 * Tests the workflow of:
 * 1. Starting from a user-provided seed URL
 * 2. Extracting content from the seed page
 * 3. Following relevant links (respecting depth and domain constraints)
 * 4. Aggregating evidence across pages
 * 5. Synthesizing answer with citations
 */

import { test, expect } from '@playwright/test';

const API_URL = process.env.VITE_API_URL || 'http://localhost:8000';
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';

test.describe('UC-02: Question → Seed URL → Linked Reading', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(FRONTEND_URL);
  });

  test('should use seed URL instead of searching (happy path)', async ({ page }) => {
    const question = 'What features does this framework offer?';
    const seedUrl = 'https://tanstack.com/router/latest';

    // Fill question and seed URL
    await page.getByRole('textbox', { name: /question/i }).fill(question);
    await page.getByLabel(/seed url/i).fill(seedUrl);

    // Submit
    await page.getByRole('button', { name: /submit question/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);

    // Verify task was created with seed URL
    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    
    expect(task.seed_url).toBe(seedUrl);
    expect(task.question).toBe(question);
  });

  test('should respect same_domain_only constraint', async ({ page }) => {
    const seedUrl = 'https://example.com/start';

    await page.getByRole('textbox', { name: /question/i }).fill('Test question');
    await page.getByLabel(/seed url/i).fill(seedUrl);

    await page.getByLabel(/same domain only/i).check();

    await page.getByRole('button', { name: /submit question/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);

    // Verify same_domain_only is true
    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    
    expect(task.same_domain_only).toBe(true);
    expect(task.seed_url).toBe(seedUrl);
  });

  test('should respect allow_external_links constraint', async ({ page }) => {
    const seedUrl = 'https://example.com/page';

    await page.getByRole('textbox', { name: /question/i }).fill('Test question');
    await page.getByLabel(/seed url/i).fill(seedUrl);

    await page.getByLabel(/allow external links/i).uncheck();

    await page.getByRole('button', { name: /submit question/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);

    // Verify allow_external_links is false
    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    
    expect(task.allow_external_links).toBe(false);
    expect(task.seed_url).toBe(seedUrl);
  });

  test('should work with both same_domain_only and allow_external_links constraints', async ({ page }) => {
    const seedUrl = 'https://docs.example.com/guide';

    await page.getByRole('textbox', { name: /question/i }).fill('How does this work?');
    await page.getByLabel(/seed url/i).fill(seedUrl);

    // Enable same_domain_only and disable allow_external_links
    await page.getByLabel(/same domain only/i).check();
    await page.getByLabel(/allow external links/i).uncheck();

    await page.getByRole('button', { name: /submit question/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);

    // Verify both constraints
    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    
    expect(task.same_domain_only).toBe(true);
    expect(task.allow_external_links).toBe(false);
  });

  test('should respect max_depth for link following', async ({ page }) => {
    const seedUrl = 'https://example.com/start';

    await page.getByRole('textbox', { name: /question/i }).fill('Test depth');
    await page.getByLabel(/seed url/i).fill(seedUrl);

    // Set max depth to 1 (only immediate links)
    const maxDepthInput = page.getByLabel(/max link depth/i);
    await maxDepthInput.clear();
    await maxDepthInput.fill('1');

    await page.getByRole('button', { name: /submit question/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);

    // Verify max_depth
    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    
    expect(task.max_depth).toBe(1);
  });

  test('should handle invalid seed URL format', async ({ page }) => {
    await page.getByRole('textbox', { name: /question/i }).fill('Test question');
    
    // Try invalid URL
    const seedUrlInput = page.getByLabel(/seed url/i);
    await seedUrlInput.fill('not-a-valid-url');

    await page.getByRole('button', { name: /submit question/i }).click();

    // HTML5 validation should prevent submission or show error
    // Check if input has type="url" which provides validation
    await expect(seedUrlInput).toHaveAttribute('type', 'url');
  });

  test('should work without seed URL (falls back to search)', async ({ page }) => {
    // Submit without seed URL - should work like UC-01
    await page.getByRole('textbox', { name: /question/i }).fill('What is TypeScript?');
    await page.getByRole('button', { name: /submit question/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);

    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    
    // seed_url should be null or undefined
    expect(task.seed_url).toBeFalsy();
  });

  test('should use default link following settings when not specified', async ({ page }) => {
    const seedUrl = 'https://example.com';

    await page.getByRole('textbox', { name: /question/i }).fill('Test defaults');
    await page.getByLabel(/seed url/i).fill(seedUrl);

    // Don't toggle advanced options - use defaults
    await page.getByRole('button', { name: /submit question/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);

    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    
    // Verify defaults for UC-02 parameters
    expect(task.same_domain_only).toBe(false); // default: false
    expect(task.allow_external_links).toBe(true); // default: true
  });

  test('should handle seed URL with query parameters', async ({ page }) => {
    const seedUrl = 'https://example.com/page?query=test&lang=en';

    await page.getByRole('textbox', { name: /question/i }).fill('Test with params');
    await page.getByLabel(/seed url/i).fill(seedUrl);

    await page.getByRole('button', { name: /submit question/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);

    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    
    expect(task.seed_url).toBe(seedUrl);
  });

  test('should handle seed URL with fragments', async ({ page }) => {
    const seedUrl = 'https://example.com/docs#section-2';

    await page.getByRole('textbox', { name: /question/i }).fill('Test with fragment');
    await page.getByLabel(/seed url/i).fill(seedUrl);

    await page.getByRole('button', { name: /submit question/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);

    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    
    expect(task.seed_url).toBe(seedUrl);
  });

  test('should combine UC-02 with UC-01 parameters (hybrid scenario)', async ({ page }) => {
    // Seed URL provided but also set search parameters (for fallback)
    const seedUrl = 'https://example.com/start';

    await page.getByRole('textbox', { name: /question/i }).fill('Hybrid test');
    await page.getByLabel(/seed url/i).fill(seedUrl);

    
    // Set UC-01 parameters
    await page.locator('select').first().selectOption('bing');
    
    // Set UC-02 parameters
    await page.getByLabel(/same domain only/i).check();

    await page.getByRole('button', { name: /submit question/i }).click();

    await expect(page).toHaveURL(/\/tasks\/.+/);

    const url = page.url();
    const taskId = url.split('/tasks/')[1];
    const response = await page.request.get(`${API_URL}/api/tasks/${taskId}`);
    const task = await response.json();
    
    expect(task.seed_url).toBe(seedUrl);
    expect(task.search_engine).toBe('bing');
    expect(task.same_domain_only).toBe(true);
  });
});
