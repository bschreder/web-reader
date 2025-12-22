import type { StreamEvent } from '@src/types/task';

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
 *
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
        const ev = JSON.parse(e.data) as StreamEvent;
        this.opts.onEvent(ev);
      } catch (err) {
        console.error('Invalid event', err);
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
