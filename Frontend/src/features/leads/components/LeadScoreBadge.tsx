interface LeadScoreBadgeProps {
  score: number | null
}

export function LeadScoreBadge({ score }: LeadScoreBadgeProps) {
  if (score === null || score === undefined) {
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium text-slate-400 bg-slate-800/60 border border-slate-700/50 italic">
        Sin score
      </span>
    )
  }

  const getScoreColor = (value: number) => {
    if (value >= 80) {
      return 'text-emerald-400 bg-emerald-950/40 border-emerald-800/50'
    }
    if (value >= 60) {
      return 'text-amber-400 bg-amber-950/40 border-amber-800/50'
    }
    return 'text-slate-300 bg-slate-800/60 border-slate-700/50'
  }

  return (
    <span
      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-mono font-bold border ${getScoreColor(
        score
      )}`}
      aria-label={`Score: ${score} de 100`}
    >
      <span>{score}</span>
      <span className="text-[10px] text-slate-500 font-normal">/100</span>
    </span>
  )
}
