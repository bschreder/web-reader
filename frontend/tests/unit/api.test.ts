import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createTask, getTask, listTasks, cancelTask } from '../../src/lib/api';

const originalFetch = globalThis.fetch;

describe('API client', () => {
  beforeEach(() => {
    globalThis.fetch = vi.fn() as unknown as typeof fetch;
  });
  afterEach(() => {
    globalThis.fetch = originalFetch;
    vi.restoreAllMocks();
  });

  it('createTask returns id', async () => {
    (globalThis.fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ id: '123' } as Record<string, unknown>),
    });
    const res = await createTask({ question: 'q' });
    expect(res.id).toBe('123');
  });

  it('getTask throws on error', async () => {
    (globalThis.fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: false,
      status: 500,
    });
    await expect(getTask('bad')).rejects.toThrow();
  });

  it('listTasks parses array', async () => {
    (globalThis.fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([] as Record<string, unknown>[]),
    });
    const res = await listTasks();
    expect(Array.isArray(res)).toBe(true);
  });

  it('cancelTask throws on error', async () => {
    (globalThis.fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: false,
      status: 404,
    });
    await expect(cancelTask('x')).rejects.toThrow();
  });
});
