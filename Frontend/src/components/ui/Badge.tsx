import React from 'react'
import { cn } from '@/lib/utils'

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'neutral' | 'success' | 'warning' | 'danger' | 'info'
  size?: 'sm' | 'md'
}

export function Badge({
  className,
  variant = 'default',
  size = 'md',
  children,
  ...props
}: BadgeProps) {
  const variants = {
    default: 'bg-slate-800 text-slate-300 border-slate-700',
    neutral: 'bg-slate-800/80 text-slate-400 border-slate-700/60',
    success: 'bg-emerald-950/70 text-emerald-300 border-emerald-800/50',
    warning: 'bg-amber-950/70 text-amber-300 border-amber-800/50',
    danger: 'bg-rose-950/70 text-rose-300 border-rose-800/50',
    info: 'bg-cyan-950/70 text-cyan-300 border-cyan-800/50',
  }

  const sizes = {
    sm: 'text-[11px] px-2 py-0.5 font-medium tracking-wide',
    md: 'text-xs px-2.5 py-1 font-semibold tracking-wide',
  }

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-md border font-medium uppercase',
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {children}
    </span>
  )
}
