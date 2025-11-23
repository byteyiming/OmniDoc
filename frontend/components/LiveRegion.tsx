'use client';

import { ReactNode } from 'react';

interface LiveRegionProps {
  children: ReactNode;
  level?: 'polite' | 'assertive' | 'off';
  atomic?: boolean;
  className?: string;
}

/**
 * LiveRegion component for announcing dynamic content changes to screen readers
 * Use for status updates, error messages, and success notifications
 */
export default function LiveRegion({
  children,
  level = 'polite',
  atomic = false,
  className,
}: LiveRegionProps) {
  return (
    <div
      role="status"
      aria-live={level}
      aria-atomic={atomic}
      className={className || 'sr-only'}
    >
      {children}
    </div>
  );
}

