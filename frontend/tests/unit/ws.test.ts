import { beforeEach, afterEach, describe, expect, it, vi } from 'vitest';
import { WebSocketManager } from '../../src/lib/ws';

describe('WebSocketManager', () => {
  let originalWebSocket: typeof WebSocket;
  let mockWebSocketInstance: {
    onmessage: ((e: MessageEvent) => void) | null;
    onclose: (() => void) | null;
    close: ReturnType<typeof vi.fn>;
  };

  beforeEach(() => {
    // Save original WebSocket
    originalWebSocket = global.WebSocket;
    
    // Create mock instance that will be returned by constructor
    mockWebSocketInstance = {
      onmessage: null,
      onclose: null,
      close: vi.fn(),
    };
    
    // Create a proper mock constructor using a class
    global.WebSocket = class MockWebSocket {
      onmessage: ((e: MessageEvent) => void) | null;
      onclose: (() => void) | null;
      close: ReturnType<typeof vi.fn>;
      
      /**
       * Initialize WebSocket mock.
       * @param {string} _url - WebSocket URL (unused in mock)
       */
      constructor(_url: string) {
        this.onmessage = mockWebSocketInstance.onmessage;
        this.onclose = mockWebSocketInstance.onclose;
        this.close = mockWebSocketInstance.close;
        // Bind instance references back to the test mock
        mockWebSocketInstance.onmessage = null;
        mockWebSocketInstance.onclose = null;
        Object.defineProperty(mockWebSocketInstance, 'onmessage', {
          get: () => this.onmessage,
          set: (v) => { this.onmessage = v; },
          configurable: true,
        });
        Object.defineProperty(mockWebSocketInstance, 'onclose', {
          get: () => this.onclose,
          set: (v) => { this.onclose = v; },
          configurable: true,
        });
      }
    } as unknown as typeof WebSocket;
  });

  afterEach(() => {
    // Restore original WebSocket
    global.WebSocket = originalWebSocket;
    vi.clearAllMocks();
  });

  it('constructs with options', (): void => {
    const mgr = new WebSocketManager({ taskId: '1', onEvent: (): void => void 0 });
    expect(mgr).toBeTruthy();
  });

  it('connects and creates WebSocket', (): void => {
    const onEvent = vi.fn();
    const mgr = new WebSocketManager({ taskId: 'test-123', onEvent });
    mgr.connect();
    // Check that WebSocket was instantiated by checking if onmessage handler was set
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    expect((mgr as any).ws).toBeTruthy();
  });

  it('calls onEvent when valid message received', (): void => {
    const onEvent = vi.fn();
    const mgr = new WebSocketManager({ taskId: 'test-123', onEvent });
    mgr.connect();

    // Simulate a valid stream event
    if (mockWebSocketInstance.onmessage) {
      mockWebSocketInstance.onmessage({ 
        data: JSON.stringify({ 
          type: 'thinking', 
          ts: Date.now(),
          message: 'Processing request'
        }) 
      } as MessageEvent);
    }

    expect(onEvent).toHaveBeenCalled();
  });

  it('calls onClose when WebSocket closes', (): void => {
    const onClose = vi.fn();
    const mgr = new WebSocketManager({ taskId: 'test-123', onEvent: (): void => {}, onClose });
    mgr.connect();

    // Simulate WebSocket close
    if (mockWebSocketInstance.onclose) {
      mockWebSocketInstance.onclose();
    }

    expect(onClose).toHaveBeenCalled();
  });

  it('closes WebSocket when close is called', (): void => {
    const mgr = new WebSocketManager({ taskId: 'test-123', onEvent: (): void => {} });
    mgr.connect();
    mgr.close();

    expect(mockWebSocketInstance.close).toHaveBeenCalled();
  });

  it('handles invalid JSON gracefully', (): void => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    const onEvent = vi.fn();
    const mgr = new WebSocketManager({ taskId: 'test-123', onEvent });
    mgr.connect();

    // Simulate invalid JSON message
    if (mockWebSocketInstance.onmessage) {
      mockWebSocketInstance.onmessage({ data: 'invalid json' } as MessageEvent);
    }

    expect(onEvent).not.toHaveBeenCalled();
    expect(consoleSpy).toHaveBeenCalledWith('Invalid event data:', expect.any(Error));
    consoleSpy.mockRestore();
  });
});
