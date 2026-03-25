import type { ZodType } from 'zod';
import { ZodError, prettifyError } from 'zod';

/**
 * Safely parse data with a Zod schema. Returns null when validation fails.
 * @param {ZodType<T>} schema - The Zod schema to validate against
 * @param {unknown} data - The data to validate
 * @returns {T | null} Parsed and validated data, or null on validation failure
 */
export function safeParseData<T>(schema: ZodType<T>, data: unknown): T | null {
  try {
    return schema.parse(data);
  } catch (error) {
    if (error instanceof ZodError) {
      console.error('Validation failed:', prettifyError(error), '\nData:', JSON.stringify(data).slice(0, 500));
    } else {
      console.error('Unexpected parse error:', error, '\nData:', JSON.stringify(data).slice(0, 500));
    }
    return null;
  }
}

