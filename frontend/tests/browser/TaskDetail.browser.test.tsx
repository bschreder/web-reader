/**
 * Browser tests for TaskDetail WebSocket event rendering.
 */

import { expect, test, vi, beforeEach } from 'vitest'
import { page } from 'vitest/browser'
import { render } from 'vitest-browser-react'
import { TaskDetail } from '~/components/TaskDetail'
import type { AgentEvent, Task } from '~/lib/types'

// Mock the API module
vi.mock('~/lib/api', () => ({
  getTask: vi.fn(),
  getScreenshotUrl: (taskId: string, index: number) => 
    `http://localhost:8000/api/tasks/${taskId}/screenshots/${index}`,
  createTask: vi.fn(),
  cancelTask: vi.fn(),
  listTasks: vi.fn(),
  getHealth: vi.fn(),
}))

// Mock the websocket module
let mockEventHandler: ((e: AgentEvent) => void) | null = null
const mockClose = vi.fn()

vi.mock('~/lib/websocket', () => ({
  connectTaskStream: vi.fn((_taskId: string, handler: (e: AgentEvent) => void): WebSocketManager => {
    mockEventHandler = handler
    return {
      close: mockClose,
      isConnected: () => true,
    }
  }),
}))

// Import after mocking
import { getTask } from '~/lib/api'
import { connectTaskStream, WebSocketManager } from '~/lib/websocket'

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
  vi.mocked(connectTaskStream).mockImplementation((_taskId, handler): WebSocketManager => {
    mockEventHandler = handler
    return {
      close: mockClose,
      isConnected: () => true,
    }
  })
})

test('TaskDetail renders loading state initially', async () => {
  render(<TaskDetail taskId="test-123" />)
  
  const spinner = page.getByRole('status', { name: /Loading/ })
  await expect.element(spinner).toBeInTheDocument()
})

test('TaskDetail displays thinking event in event log', async () => {
  render(<TaskDetail taskId="test-123" />)
  
  // Wait briefly for render
  await new Promise(resolve => setTimeout(resolve, 100))
  
  // Simulate thinking event
  mockEventHandler?.({
    type: 'agent:thinking',
    content: 'Analyzing the question about quantum computing...',
    timestamp: '2024-01-01T00:00:01Z',
  })
  
  await new Promise(resolve => setTimeout(resolve, 100))
  
  const thinkingText = page.getByText(/Analyzing the question/)
  await expect.element(thinkingText).toBeVisible()
})

test('TaskDetail displays answer on complete event', async () => {
  render(<TaskDetail taskId="test-123" />)
  
  await new Promise(resolve => setTimeout(resolve, 100))
  
  // Simulate complete event with answer
  mockEventHandler?.({
    type: 'agent:complete',
    answer: 'Quantum computing uses quantum mechanics to process information.',
    citations: [{ url: 'https://example.com', title: 'Quantum Intro' }],
    screenshots: [],
    metadata: {},
  })
  
  await new Promise(resolve => setTimeout(resolve, 100))
  
  const answer = page.getByText(/Quantum computing uses quantum mechanics/)
  await expect.element(answer).toBeVisible()
  
  const citation = page.getByText(/Quantum Intro/)
  await expect.element(citation).toBeVisible()
})

test('TaskDetail handles error event', async () => {
  render(<TaskDetail taskId="test-123" />)
  
  await new Promise(resolve => setTimeout(resolve, 100))
  
  // Simulate error event
  mockEventHandler?.({
    type: 'agent:error',
    error: 'Failed to connect to search service',
    timestamp: '2024-01-01T00:00:02Z',
  })
  
  await new Promise(resolve => setTimeout(resolve, 100))
  
  const errorMsg = page.getByText(/Failed to connect/)
  await expect.element(errorMsg).toBeVisible()
})

test('TaskDetail closes WebSocket on unmount', async () => {
  const result = await render(<TaskDetail taskId="test-123" />)
  
  await new Promise(resolve => setTimeout(resolve, 100))
  
  result.unmount()
  
  expect(mockClose).toHaveBeenCalled()
})
