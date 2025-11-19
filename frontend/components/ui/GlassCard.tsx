'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  hoverEffect?: boolean;
}

export function GlassCard({ 
  children, 
  className, 
  hoverEffect = false,
  ...props 
}: GlassCardProps) {
  return (
    <div 
      className={cn(
        "glass-panel rounded-2xl p-6 transition-all duration-300",
        hoverEffect && "hover:bg-white/5 hover:border-indigo-500/30 hover:shadow-[0_0_30px_rgba(99,102,241,0.15)]",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

