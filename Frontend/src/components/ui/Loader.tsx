import { cn } from '@/lib/utils'

export function Loader({
  className,
  label = 'Cargando datos...',
}: {
  className?: string
  label?: string
}) {
  return (
    <div className={cn('flex flex-col items-center justify-center p-8 text-center', className)}>
      <div className="w-8 h-8 border-3 border-amber-500/20 border-t-amber-500 rounded-full animate-spin mb-3" />
      {label && <p className="text-xs text-slate-400 font-medium">{label}</p>}
    </div>
  )
}

export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn('animate-pulse bg-slate-800/80 rounded-md', className)}
    />
  )
}
