/**
 * Input component with label, error, and helper text support.
 */

import { type ComponentPropsWithoutRef, forwardRef } from 'react';

interface InputProps extends ComponentPropsWithoutRef<'input'> {
  /** Input label */
  label?: string;
  /** Error message */
  error?: string;
  /** Helper text shown below input */
  helperText?: string;
  /** Container className */
  containerClassName?: string;
}

/**
 * Styled input component with label and validation support.
 * 
 * @example
 * ```tsx
 * <Input
 *   label="Email"
 *   type="email"
 *   error={errors.email}
 *   helperText="We'll never share your email."
 * />
 * ```
 */
export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, containerClassName = '', className = '', id, ...props }, ref) => {
    const inputId = id || `input-${label?.toLowerCase().replace(/\s+/g, '-')}`;
    const hasError = Boolean(error);
    
    const inputStyles = hasError
      ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
      : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500';
    
    const inputClasses = `block w-full rounded-md shadow-sm sm:text-sm px-3 py-2 focus:outline-none focus:ring-2 ${inputStyles} ${className}`;
    
    return (
      <div className={containerClassName}>
        {label && (
          <label htmlFor={inputId} className="block text-sm font-medium text-gray-700 mb-1">
            {label}
            {props.required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={inputClasses}
          aria-invalid={hasError}
          aria-describedby={
            error ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined
          }
          {...props}
        />
        {error && (
          <p id={`${inputId}-error`} className="mt-1 text-sm text-red-600" role="alert">
            {error}
          </p>
        )}
        {!error && helperText && (
          <p id={`${inputId}-helper`} className="mt-1 text-sm text-gray-500">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
