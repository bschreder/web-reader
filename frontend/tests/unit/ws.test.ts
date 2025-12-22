import { describe, expect, it } from 'vitest';
import { WebSocketManager } from '../../src/lib/ws';

// Simple construction test to cover basic logic

describe('WebSocketManager', (): void => {
  it('constructs with options', (): void => {
    const mgr = new WebSocketManager({ taskId: '1', onEvent: (): void => void 0 });
    expect(mgr).toBeTruthy();
  });
});
