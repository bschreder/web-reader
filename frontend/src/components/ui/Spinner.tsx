/**
 * Loading spinner component.
 */

import { type ComponentPropsWithoutRef, forwardRef } from 'react';

interface SpinnerProps extends ComponentPropsWithoutRef<'div'> {
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Center in container */
  centered?: boolean;
}

/**
 * Animated loading spinner.
 * 
 * @example
 * ```tsx
 * <Spinner size="lg" centered />
 * ```
 */
export const Spinner = forwardRef<HTMLDivElement, SpinnerProps>(
  ({ size = 'md', centered = false, className = '', ...props }, ref) => {
    const sizeStyles = {
      sm: 'h-4 w-4',
      md: 'h-8 w-8',
      lg: 'h-12 w-12',
    };
    
    const spinnerClasses = `animate-spin rounded-full border-b-2 border-blue-600 ${sizeStyles[size]}`;
    const containerClasses = centered ? 'flex items-center justify-center' : '';
    
    return (
      <div ref={ref} className={`${containerClasses} ${className}`} {...props}>
        <div className={spinnerClasses} role="status" aria-label="Loading">
          <span className="sr-only">Loading...</span>
        </div>
      </div>
    );
  }
);

Spinner.displayName = 'Spinner';
