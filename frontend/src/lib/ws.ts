import type { StreamEvent } from '@src/schemas/task.schema';
import { StreamEventSchema } from '@src/schemas/task.schema';
import { safeParseData } from './safeParseData';

const WS_URL = import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000';

/**
 * Options for WebSocketManager initialization.
 */
export interface WebSocketManagerOptions {
  taskId: string;
  onEvent: (ev: StreamEvent) => void;
  onClose?: () => void;
}

/**
 * WebSocket manager for handling real-time task stream events.
 */
export class WebSocketManager {
  private ws?: WebSocket;
  private readonly opts: WebSocketManagerOptions;

  /**
   * Create a new WebSocket manager.
   * @param {WebSocketManagerOptions} opts - Configuration options
   */
  constructor(opts: WebSocketManagerOptions) {
    this.opts = opts;
  }

  /**
   * Connect to the WebSocket server.
   * @returns {void}
   */
  connect(): void {
    const url = `${WS_URL}/api/tasks/${this.opts.taskId}/stream`;
    this.ws = new WebSocket(url);
    this.ws.onerror = (ev): void => {
      console.error('websocket error', ev);
    };
    this.ws.onmessage = (e: MessageEvent<string>): void => {
      let rawData: unknown;
      try {
        rawData = JSON.parse(e.data);
      } catch (err) {
        console.error('Invalid event data:', err);
        console.error('Received data:', e.data);
        return;
      }

      // Fill missing required fields with sensible defaults
      if (!rawData || typeof rawData !== 'object') {
        console.warn('Dropped invalid WS event: not an object', rawData);
        return;
      }

      const obj = rawData as Record<string, unknown>;
      if (!obj.taskId) obj.taskId = this.opts.taskId;
      if (!obj.timestamp) obj.timestamp = new Date().toISOString();

      const ev = safeParseData(StreamEventSchema, obj);
      if (!ev) {
        console.warn('Dropped invalid WS event', obj);
        return;
      }

      this.opts.onEvent(ev);
    };
    this.ws.onclose = (): void => this.opts.onClose?.();
  }

  /**
   * Close the WebSocket connection.
   * @returns {void}
   */
  close(): void {
    this.ws?.close();
  }
}
