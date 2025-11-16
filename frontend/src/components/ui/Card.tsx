/**
 * Card container component for grouping related content.
 */

import { type ComponentPropsWithoutRef, type ReactNode, forwardRef } from 'react';

interface CardProps extends ComponentPropsWithoutRef<'div'> {
  /** Card content */
  children: ReactNode;
  /** Add hover effect */
  hoverable?: boolean;
}

/**
 * Card component for content grouping.
 * 
 * @example
 * ```tsx
 * <Card hoverable>
 *   <CardHeader>
 *     <CardTitle>Task Details</CardTitle>
 *   </CardHeader>
 *   <CardContent>
 *     <p>Task information...</p>
 *   </CardContent>
 * </Card>
 * ```
 */
export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ hoverable = false, className = '', children, ...props }, ref) => {
    const hoverStyles = hoverable ? 'hover:shadow-lg transition-shadow' : '';
    const classes = `bg-white rounded-lg border border-gray-200 shadow-sm ${hoverStyles} ${className}`;
    
    return (
      <div ref={ref} className={classes} {...props}>
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';

interface CardHeaderProps extends ComponentPropsWithoutRef<'div'> {
  children: ReactNode;
}

export const CardHeader = forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className = '', children, ...props }, ref) => {
    return (
      <div ref={ref} className={`px-6 py-4 border-b border-gray-200 ${className}`} {...props}>
        {children}
      </div>
    );
  }
);

CardHeader.displayName = 'CardHeader';

interface CardTitleProps extends ComponentPropsWithoutRef<'h3'> {
  children: ReactNode;
}

export const CardTitle = forwardRef<HTMLHeadingElement, CardTitleProps>(
  ({ className = '', children, ...props }, ref) => {
    return (
      <h3 ref={ref} className={`text-lg font-semibold text-gray-900 ${className}`} {...props}>
        {children}
      </h3>
    );
  }
);

CardTitle.displayName = 'CardTitle';

interface CardContentProps extends ComponentPropsWithoutRef<'div'> {
  children: ReactNode;
}

export const CardContent = forwardRef<HTMLDivElement, CardContentProps>(
  ({ className = '', children, ...props }, ref) => {
    return (
      <div ref={ref} className={`px-6 py-4 ${className}`} {...props}>
        {children}
      </div>
    );
  }
);

CardContent.displayName = 'CardContent';

interface CardFooterProps extends ComponentPropsWithoutRef<'div'> {
  children: ReactNode;
}

export const CardFooter = forwardRef<HTMLDivElement, CardFooterProps>(
  ({ className = '', children, ...props }, ref) => {
    return (
      <div ref={ref} className={`px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-lg ${className}`} {...props}>
        {children}
      </div>
    );
  }
);

CardFooter.displayName = 'CardFooter';
