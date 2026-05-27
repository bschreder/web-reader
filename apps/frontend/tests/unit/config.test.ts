import { describe, expect, it } from 'vitest';
import { appConfig, isServer } from '../../src/lib/config';

describe('config', () => {
  it('isServer is boolean', () => {
    expect(typeof isServer).toBe('boolean');
  });

  it('appConfig has apiUrl', () => {
    expect(typeof appConfig.apiUrl).toBe('string');
  });

  it('appConfig has wsUrl', () => {
    expect(typeof appConfig.wsUrl).toBe('string');
  });

  it('appConfig has logLevel', () => {
    expect(appConfig.logLevel).toBeTruthy();
    expect(['debug', 'info', 'warn', 'error']).toContain(appConfig.logLevel);
  });

  it('appConfig has logTarget', () => {
    expect(appConfig.logTarget).toBeTruthy();
    expect(typeof appConfig.logTarget).toBe('string');
  });

  it('appConfig has pollIntervalMs', () => {
    expect(appConfig.pollIntervalMs).toBeTypeOf('number');
    expect(appConfig.pollIntervalMs).toBeGreaterThan(0);
  });
});
