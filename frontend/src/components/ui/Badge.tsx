/**
 * Badge component for status indicators and labels.
 */

import { type ComponentPropsWithoutRef, type ReactNode, forwardRef } from 'react';

interface BadgeProps extends ComponentPropsWithoutRef<'span'> {
  /** Badge variant based on semantic meaning */
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
  /** Size variant */
  size?: 'sm' | 'md';
  /** Badge content */
  children: ReactNode;
}

/**
 * Badge component for status and labels.
 * 
 * @example
 * ```tsx
 * <Badge variant="success">Completed</Badge>
 * <Badge variant="warning" size="sm">Pending</Badge>
 * ```
 */
export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ variant = 'default', size = 'md', className = '', children, ...props }, ref) => {
    const baseStyles = 'inline-flex items-center font-medium rounded-full';
    
    const variantStyles = {
      default: 'bg-gray-100 text-gray-800',
      success: 'bg-green-100 text-green-800',
      warning: 'bg-yellow-100 text-yellow-800',
      danger: 'bg-red-100 text-red-800',
      info: 'bg-blue-100 text-blue-800',
    };
    
    const sizeStyles = {
      sm: 'px-2 py-0.5 text-xs',
      md: 'px-2.5 py-1 text-sm',
    };
    
    const classes = `${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`;
    
    return (
      <span ref={ref} className={classes} {...props}>
        {children}
      </span>
    );
  }
);

Badge.displayName = 'Badge';
