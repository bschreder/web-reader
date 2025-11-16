/**
 * Alert component for messages and notifications.
 */

import { type ComponentPropsWithoutRef, type ReactNode, forwardRef } from 'react';

interface AlertProps extends ComponentPropsWithoutRef<'div'> {
  /** Alert variant based on semantic meaning */
  variant?: 'info' | 'success' | 'warning' | 'danger';
  /** Alert title */
  title?: string;
  /** Alert content */
  children: ReactNode;
  /** Show close button */
  onClose?: () => void;
}

/**
 * Alert component for displaying messages.
 * 
 * @example
 * ```tsx
 * <Alert variant="success" title="Success!">
 *   Task completed successfully.
 * </Alert>
 * ```
 */
export const Alert = forwardRef<HTMLDivElement, AlertProps>(
  ({ variant = 'info', title, children, onClose, className = '', ...props }, ref) => {
    const variantStyles = {
      info: 'bg-blue-50 border-blue-200 text-blue-800',
      success: 'bg-green-50 border-green-200 text-green-800',
      warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
      danger: 'bg-red-50 border-red-200 text-red-800',
    };
    
    const iconPaths = {
      info: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
      success: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
      warning: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
      danger: 'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z',
    };
    
    const classes = `rounded-lg border p-4 ${variantStyles[variant]} ${className}`;
    
    return (
      <div ref={ref} className={classes} role="alert" {...props}>
        <div className="flex items-start">
          <svg
            className="h-5 w-5 mr-3 flex-shrink-0"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={iconPaths[variant]} />
          </svg>
          <div className="flex-1">
            {title && <h3 className="font-semibold mb-1">{title}</h3>}
            <div className="text-sm">{children}</div>
          </div>
          {onClose && (
            <button
              type="button"
              className="ml-3 -mr-1 -mt-1 flex-shrink-0 inline-flex rounded-md p-1.5 hover:bg-black/5 focus:outline-none focus:ring-2 focus:ring-offset-2"
              onClick={onClose}
              aria-label="Close alert"
            >
              <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          )}
        </div>
      </div>
    );
  }
);

Alert.displayName = 'Alert';
