import React, {JSX} from 'react';
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { cleanup, render } from 'vitest-browser-react';
import { userEvent } from 'vitest/browser';
import TaskForm from '@src/components/TaskForm';
import { RouterProvider, createRouter, createRootRoute, createMemoryHistory } from '@tanstack/react-router';
import { AdvancedOptionsProvider } from '@src/lib/advanced-options-context';
import { createTask } from '@src/lib/api';


// Mock the createTask API function before importing TaskForm
vi.mock('@src/lib/api', () => ({
  createTask: vi.fn().mockResolvedValue({ taskId: 'test-task-123' }),
}));

/**
 * Mount TaskForm component with required Router and AdvancedOptionsProvider.
 * @returns {JSX.Element} The React component
 */
function App(): JSX.Element {
  const rootRoute = createRootRoute({ component: () => <TaskForm /> });
  const router = createRouter({ 
    routeTree: rootRoute, 
    history: createMemoryHistory({ initialEntries: ['/'] }),
  });
  return (
    <AdvancedOptionsProvider>
      <RouterProvider router={router} />
    </AdvancedOptionsProvider>
  );
}

describe('TaskForm (browser)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders a textarea and button', async () => {
    const screen = await render(<App />);
    
    // Wait for router to initialize and component to be fully rendered
    await expect.element(screen.getByTestId('question-textarea')).toBeVisible();
    await expect.element(screen.getByTestId('submit-button')).toBeVisible();
    
    await cleanup();
  });

  it('fires onSubmit handler when Submit Research Task button is clicked', async () => {   
    const screen = await render(<App />);

    const questionTextarea = screen.getByTestId('question-textarea');
    await expect.element(questionTextarea).toBeVisible();
    
    // Fill in the question field
    await questionTextarea.fill('What is the capital of France?');

    // Click the Submit Research Task button
    const submitButton = screen.getByTestId('submit-button');
    await submitButton.click();

    // Verify that createTask was called with the correct payload
    await expect(createTask).toHaveBeenCalledOnce();
    await expect(createTask).toHaveBeenCalledWith(
      expect.objectContaining({
        question: 'What is the capital of France?',
      })
    );

    await cleanup();
  });

  it('submits form and verifies onSubmit firing, createTask call with all parameters', async () => {
    const screen = await render(<App />);

    const questionTextarea = screen.getByTestId('question-textarea');
    await expect.element(questionTextarea).toBeVisible();
    
    // Fill in the question field with test question
    await questionTextarea.fill('What is the PE ratio of CCL?');

    // Get the submit button
    const submitButton = screen.getByTestId('submit-button');
    await expect.element(submitButton).toBeVisible();

    // Click the submit button to trigger form submission and onSubmit handler
    await submitButton.click();

    // Verify that onSubmit handler was executed by checking createTask was called exactly once
    await expect(createTask).toHaveBeenCalledOnce();

    // Verify createTask was called with the correct question and all advanced option parameters
    // This confirms that the onSubmit handler properly collected all form state
    await expect(createTask).toHaveBeenCalledWith(
      expect.objectContaining({
        question: 'What is the PE ratio of CCL?',
        seedUrl: undefined,
        searchEngine: expect.any(String),
        maxResults: expect.any(Number),
        safeMode: expect.any(Boolean),
        maxDepth: expect.any(Number),
        maxPages: expect.any(Number),
        timeBudget: expect.any(Number),
        sameDomainOnly: expect.any(Boolean),
        allowExternalLinks: expect.any(Boolean),
      })
    );

    await cleanup();
  });

  it('submits form when Ctrl+Enter key is pressed in question textarea', async () => {
    const screen = await render(<App />);

    const questionTextarea = screen.getByTestId('question-textarea');
    await expect.element(questionTextarea).toBeVisible();
    
    // Fill in the question field and press Ctrl+Enter to submit
    await userEvent.click(questionTextarea);
    await userEvent.keyboard('What is the capital of France?{Control>}{Enter}{/Control}');

    // Verify that createTask was called with the correct payload
    await expect(createTask).toHaveBeenCalledOnce();
    await expect(createTask).toHaveBeenCalledWith(
      expect.objectContaining({
        question: 'What is the capital of France?',
      })
    );

    await cleanup();
  });

  it('submits form when Enter key is pressed in seed URL input', async () => {
    const screen = await render(<App />);

    const questionTextarea = screen.getByTestId('question-textarea');
    const seedUrlInput = screen.getByTestId('seed-url-input');
    
    await expect.element(questionTextarea).toBeVisible();
    await expect.element(seedUrlInput).toBeVisible();
    
    // Fill in question field
    await userEvent.click(questionTextarea);
    await userEvent.keyboard('What is quantum computing?');
    
    // Fill in seed URL field and press Enter to submit
    await userEvent.click(seedUrlInput);
    await userEvent.keyboard('https://example.com{Enter}');

    // Verify that createTask was called with the correct payload
    await expect(createTask).toHaveBeenCalledOnce();
    await expect(createTask).toHaveBeenCalledWith(
      expect.objectContaining({
        question: 'What is quantum computing?',
        seedUrl: 'https://example.com',
      })
    );

    await cleanup();
  });
});
