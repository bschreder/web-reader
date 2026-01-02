import type { StreamEvent } from '@src/types/task';
import { StreamEventSchema } from '@src/schemas/task.schema';

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
    this.ws.onmessage = (e: MessageEvent<string>): void => {
      try {
        const rawData = JSON.parse(e.data);
        // Validate stream event with zod
        const ev = StreamEventSchema.parse(rawData);
        this.opts.onEvent(ev);
      } catch (err) {
        console.error('Invalid event data:', err);
      }
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
