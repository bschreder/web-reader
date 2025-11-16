import { describe, it, expect } from 'vitest'
import { APIError } from '../../src/lib/api'

// Minimal sanity test for APIError construction

describe('APIError', () => {
  it('captures message and status', () => {
    const err = new APIError('boom', 500)
    expect(err.message).toBe('boom')
    expect(err.status).toBe(500)
    expect(err.name).toBe('APIError')
  })
})
