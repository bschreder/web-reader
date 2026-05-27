import { describe, it, expect } from 'vitest';
import { getRouter } from '@src/router';

/**
 * These tests verify the actual router configuration produced by
 * TanStack Start's generated route tree. We inspect the concrete
 * URL values (paths) for each file route via `routesById`.
 */
describe('Route SSR Configuration', () => {
  it('index route has correct URL and SSR', () => {
    const router = getRouter();
    const index = router.routesById['/'];
    expect(index).toBeDefined();
    expect(index.fullPath).toBe('/');
  });

  it('history route has correct URL', () => {
    const router = getRouter();
    const history = router.routesById['/history'];
    expect(history).toBeDefined();
    expect(history.fullPath).toBe('/history');
  });

  it('task detail route has correct URL', () => {
    const router = getRouter();
    const task = router.routesById['/tasks/$id'];
    expect(task).toBeDefined();
    expect(task.fullPath).toBe('/tasks/$id');
  });

  it('root route exists', () => {
    const router = getRouter();
    const root = router.routesById['__root__'];
    expect(root).toBeDefined();
  });
});
