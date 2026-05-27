import { JSX, useState } from 'react';
import { CreateTaskRequestSchema } from '@src/schemas/task.schema';
import type { CreateTaskRequest } from '@src/types/task';
import { ZodError } from 'zod';

/**
 * Example component demonstrating zod validation for form inputs.
 * This shows best practices for using zod with user input validation.
 * @returns {JSX.Element} The task form with validation
 */
export function TaskFormExample(): JSX.Element {
  const [formData, setFormData] = useState<Partial<CreateTaskRequest>>({
    question: '',
    seedUrl: '',
    maxDepth: undefined,
    maxPages: undefined,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  /**
   * Handle form submission with zod validation
   * @param {React.FormEvent} e - Form event
   * @returns {Promise<void>}
   */
  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    setErrors({});

    // Validate form data with zod
    const result = CreateTaskRequestSchema.safeParse(formData);

    if (!result.success) {
      // Extract validation errors
      const fieldErrors: Record<string, string> = {};
      result.error.issues.forEach((issue) => {
        const path = issue.path.join('.');
        fieldErrors[path] = issue.message;
      });
      setErrors(fieldErrors);
      return;
    }

    // Data is valid, proceed with submission
    setIsSubmitting(true);
    try {
      console.log('Valid data:', result.data);
      // await createTask(result.data);
    } catch (err) {
      if (err instanceof ZodError) {
        console.error('Validation error:', err.issues);
      } else {
        console.error('Submission error:', err);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Handle input changes with real-time validation
   * @param {keyof CreateTaskRequest} field - The field to update
   * @param {string | number | boolean} value - The new value
   * @returns {void}
   */
  const handleChange = (field: keyof CreateTaskRequest, value: string | number | boolean): void => {
    setFormData((prev) => ({ ...prev, [field]: value }));

    // Optional: Real-time validation for individual fields
    try {
      const fieldSchema = CreateTaskRequestSchema.shape[field];
      if (fieldSchema) {
        fieldSchema.parse(value);
        // Clear error if validation passes
        setErrors((prev) => {
          const newErrors = { ...prev };
          delete newErrors[field];
          return newErrors;
        });
      }
    } catch (err) {
      if (err instanceof ZodError) {
        setErrors((prev) => ({
          ...prev,
          [field]: err.issues[0]?.message ?? 'Invalid value',
        }));
      }
    }
  };

  return (
    <div className="max-w-md mx-auto p-6">
      <h2 className="text-2xl font-bold mb-4">Task Form with Zod Validation</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Question field */}
        <div>
          <label className="block text-sm font-medium mb-1" htmlFor="question">
            Question *
          </label>
          <input
            id="question"
            type="text"
            value={formData.question}
            onChange={(e) => handleChange('question', e.target.value)}
            className={`w-full px-3 py-2 border rounded ${
              errors.question ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="What would you like to research?"
          />
          {errors.question && (
            <p className="text-red-500 text-sm mt-1">{errors.question}</p>
          )}
        </div>

        {/* Seed URL field */}
        <div>
          <label className="block text-sm font-medium mb-1" htmlFor="seedUrl">
            Seed URL
          </label>
          <input
            id="seedUrl"
            type="url"
            value={formData.seedUrl}
            onChange={(e) => handleChange('seedUrl', e.target.value)}
            className={`w-full px-3 py-2 border rounded ${
              errors.seedUrl ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="https://example.com"
          />
          {errors.seedUrl && (
            <p className="text-red-500 text-sm mt-1">{errors.seedUrl}</p>
          )}
        </div>

        {/* Max Pages field */}
        <div>
          <label className="block text-sm font-medium mb-1" htmlFor="maxPages">
            Max Pages
          </label>
          <input
            id="maxPages"
            type="number"
            value={formData.maxPages ?? ''}
            onChange={(e) => {
              const val = e.target.value ? parseInt(e.target.value, 10) : undefined;
              handleChange('maxPages', val as number);
            }}
            className={`w-full px-3 py-2 border rounded ${
              errors.maxPages ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="10"
            min="1"
          />
          {errors.maxPages && (
            <p className="text-red-500 text-sm mt-1">{errors.maxPages}</p>
          )}
        </div>

        {/* Submit button */}
        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? 'Submitting...' : 'Create Task'}
        </button>
      </form>

      {/* Display all validation errors */}
      {Object.keys(errors).length > 0 && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded">
          <h3 className="text-red-800 font-medium mb-2">Validation Errors:</h3>
          <ul className="list-disc list-inside text-red-600 text-sm">
            {Object.entries(errors).map(([field, message]) => (
              <li key={field}>
                <strong>{field}:</strong> {message}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
