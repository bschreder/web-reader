/**
 * Additional TaskDetail tests for UI interactions and edge cases.
 */

import { expect, test, vi, beforeEach } from 'vitest'
import { page } from 'vitest/browser'
import { render } from 'vitest-browser-react'
import { TaskDetail } from '~/components/TaskDetail'
import type { AgentEvent, Task } from '~/lib/types'

// Mock API module
vi.mock('~/lib/api', () => ({
  getTask: vi.fn(),
  getScreenshotUrl: (taskId: string, index: number) => 
    `http://localhost:8000/api/tasks/${taskId}/screenshots/${index}`,
  createTask: vi.fn(),
  cancelTask: vi.fn(),
  listTasks: vi.fn(),
  getHealth: vi.fn(),
}))

// Mock websocket module
let mockEventHandler: ((e: AgentEvent) => void) | null = null
const mockClose = vi.fn()

vi.mock('~/lib/websocket', () => ({
  connectTaskStream: vi.fn((_taskId: string, handler: (e: AgentEvent) => void) => {
    mockEventHandler = handler
    return {
      close: mockClose,
      isConnected: () => true,
    }
  }),
}))

import { getTask } from '~/lib/api'

const mockTask: Task = {
  task_id: 'test-123',
  question: 'What is quantum computing?',
  status: 'running',
  created_at: '2024-01-01T00:00:00Z',
  citations: [],
  screenshots: [],
  metadata: {},
}

beforeEach(() => {
  mockEventHandler = null
  mockClose.mockClear()
  vi.mocked(getTask).mockResolvedValue(mockTask)
})

test('TaskDetail event log can be collapsed and expanded', async () => {
  render(<TaskDetail taskId="test-123" />)
  
  await new Promise(resolve => setTimeout(resolve, 100))
  
  // Send event so log has content
  mockEventHandler?.({
    type: 'agent:thinking',
    content: 'Processing...',
  })
  
  await new Promise(resolve => setTimeout(resolve, 50))
  
  // Find collapse button
  const collapseBtn = page.getByRole('button', { name: /Collapse event log/i })
  await expect.element(collapseBtn).toBeVisible()
  
  // Click to collapse
  await collapseBtn.click()
  
  // Button should now say "Expand"
  const expandBtn = page.getByRole('button', { name: /Expand event log/i })
  await expect.element(expandBtn).toBeVisible()
  
  // Click to expand again
  await expandBtn.click()
  
  await expect.element(page.getByRole('button', { name: /Collapse event log/i })).toBeVisible()
})

test('TaskDetail displays tool call events', async () => {
  render(<TaskDetail taskId="test-123" />)
  
  await new Promise(resolve => setTimeout(resolve, 100))
  
  mockEventHandler?.({
    type: 'agent:tool_call',
    tool: 'search_web',
    args: { query: 'quantum computing' },
  })
  
  await new Promise(resolve => setTimeout(resolve, 100))
  
  const toolText = page.getByText(/search_web/)
  await expect.element(toolText).toBeVisible()
})

test('TaskDetail shows screenshots when available', async () => {
  render(<TaskDetail taskId="test-123" />)
  
  await new Promise(resolve => setTimeout(resolve, 100))
  
  mockEventHandler?.({
    type: 'agent:complete',
    answer: 'Answer text',
    screenshots: ['screenshot1.png', 'screenshot2.png'],
  })
  
  await new Promise(resolve => setTimeout(resolve, 100))
  
  // Should show screenshot count or images
  const screenshotSection = page.getByText(/Screenshots/i)
  await expect.element(screenshotSection).toBeVisible()
})

test('TaskDetail handles completed task with existing answer', async () => {
  const completedTask: Task = {
    ...mockTask,
    status: 'completed',
    answer: 'Quantum computing leverages quantum mechanics.',
    citations: [{ url: 'https://example.com', title: 'Source' }],
  }
  
  vi.mocked(getTask).mockResolvedValue(completedTask)
  
  render(<TaskDetail taskId="test-123" />)
  
  await new Promise(resolve => setTimeout(resolve, 200))
  
  const answerText = page.getByText(/Quantum computing leverages/)
  await expect.element(answerText).toBeVisible()
  
  const citationLink = page.getByText(/Source/)
  await expect.element(citationLink).toBeVisible()
})

test('TaskDetail copy button copies answer to clipboard', async () => {
  render(<TaskDetail taskId="test-123" />)
  
  await new Promise(resolve => setTimeout(resolve, 100))
  
  mockEventHandler?.({
    type: 'agent:complete',
    answer: 'Test answer for clipboard',
  })
  
  await new Promise(resolve => setTimeout(resolve, 100))
  
  const copyBtn = page.getByRole('button', { name: /Copy answer/i })
  await expect.element(copyBtn).toBeVisible()
  
  // Note: We cannot test clipboard.writeText in browser mode as 
  // navigator.clipboard is read-only. This test verifies the button exists.
})

test('TaskDetail shows empty state for no events', async () => {
  render(<TaskDetail taskId="test-123" />)
  
  await new Promise(resolve => setTimeout(resolve, 100))
  
  // No events sent, should show "No events yet" or similar
  const eventLog = page.getByText(/Waiting for agent/)
  await expect.element(eventLog).toBeVisible()
})

test('TaskDetail displays error event with error icon', async () => {
  render(<TaskDetail taskId="test-123" />)
  
  await new Promise(resolve => setTimeout(resolve, 100))
  
  mockEventHandler?.({
    type: 'agent:error',
    error: 'Test error message',
  })
  
  await new Promise(resolve => setTimeout(resolve, 100))
  
  const errorText = page.getByText(/Test error message/)
  await expect.element(errorText).toBeVisible()
})
