import type { AgentEvent } from './types'

const WS_BASE_URL = import.meta.env?.VITE_WS_URL || 'ws://localhost:8000'

export type EventHandler = (event: AgentEvent) => void

export class WebSocketManager {
  private ws: WebSocket | null = null
  private handlers: EventHandler[] = []
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private taskId: string
  private shouldReconnect = true

  constructor(taskId: string) {
    this.taskId = taskId
  }

  connect(onEvent: EventHandler): void {
    this.handlers.push(onEvent)
    this.shouldReconnect = true
    this._connect()
  }

  private _connect(): void {
    const url = `${WS_BASE_URL}/api/tasks/${this.taskId}/stream`
    try {
      this.ws = new WebSocket(url)
      this.ws.onopen = () => {
        this.reconnectAttempts = 0
      }
      this.ws.onmessage = (event) => {
        try {
          const data: AgentEvent = JSON.parse(event.data)
          this.handlers.forEach((h) => h(data))
          if (data.type === 'agent:complete' || data.type === 'task:complete') this.shouldReconnect = false
        } catch (e) {
          console.error('WS parse error', e)
        }
      }
      this.ws.onerror = (e) => console.error('WS error', e)
      this.ws.onclose = () => {
        this.ws = null
        if (this.shouldReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++
          const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
          setTimeout(() => this.shouldReconnect && this._connect(), delay)
        } else if (this.reconnectAttempts >= this.maxReconnectAttempts) {
          this.handlers.forEach((h) => h({ type: 'error', error: 'Maximum reconnection attempts reached' }))
        }
      }
    } catch (error) {
      this.handlers.forEach((h) => h({ type: 'error', error: error instanceof Error ? error.message : 'WS failed' }))
    }
  }

  close(): void {
    this.shouldReconnect = false
    if (this.ws) this.ws.close()
    this.ws = null
    this.handlers = []
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
}

export function connectTaskStream(taskId: string, onEvent: EventHandler): WebSocketManager {
  const m = new WebSocketManager(taskId)
  m.connect(onEvent)
  return m
}
