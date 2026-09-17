import { cn } from '@/lib/utils'

export function ScoreIndicator({
  score,
  size = 'md',
  showLabel = true,
}: {
  score: number
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
}) {
  const getColorScheme = (val: number) => {
    if (val >= 80) {
      return {
        text: 'text-emerald-400',
        bg: 'bg-emerald-950/40',
        border: 'border-emerald-700/50',
        bar: 'bg-gradient-to-r from-emerald-500 to-teal-400',
      }
    }
    if (val >= 60) {
      return {
        text: 'text-amber-400',
        bg: 'bg-amber-950/40',
        border: 'border-amber-700/50',
        bar: 'bg-gradient-to-r from-amber-500 to-yellow-400',
      }
    }
    return {
      text: 'text-slate-400',
      bg: 'bg-slate-900/40',
      border: 'border-slate-800',
      bar: 'bg-gradient-to-r from-slate-500 to-slate-400',
    }
  }

  const colors = getColorScheme(score)

  if (size === 'sm') {
    return (
      <div className="flex items-center gap-1.5">
        <span className={cn('text-xs font-bold font-mono', colors.text)}>
          {score}
        </span>
        <span className="text-[10px] text-slate-400">pts</span>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-1 min-w-[90px]">
      <div className="flex items-center justify-between">
        {showLabel && (
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
            Score IA
          </span>
        )}
        <span className={cn('font-bold font-mono text-sm leading-none', colors.text)}>
          {score}<span className="text-[10px] text-slate-400 font-normal">/100</span>
        </span>
      </div>
      <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
        <div
          className={cn('h-full rounded-full transition-all duration-500', colors.bar)}
          style={{ width: `${Math.min(score, 100)}%` }}
        />
      </div>
    </div>
  )
}
