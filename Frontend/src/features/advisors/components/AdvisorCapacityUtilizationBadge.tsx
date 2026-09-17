interface AdvisorCapacityUtilizationBadgeProps {
  percent: number | null
}

export function AdvisorCapacityUtilizationBadge({
  percent,
}: AdvisorCapacityUtilizationBadgeProps) {
  if (percent === null || percent === undefined) {
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium text-slate-400 bg-slate-800/60 border border-slate-700/50 italic">
        No disponible
      </span>
    )
  }

  // Criterios de capacidad con texto y porcentaje explícito, no solo color
  if (percent > 100) {
    return (
      <span
        className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-950/70 text-rose-300 border border-rose-800/60"
        aria-label={`Sobrecarga operativa estimada: ${percent}%`}
      >
        <span>Sobrecarga</span>
        <span className="font-mono">({percent}%)</span>
      </span>
    )
  }

  if (percent >= 50) {
    return (
      <span
        className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-950/70 text-emerald-300 border border-emerald-800/60"
        aria-label={`Utilización operativa estimada: ${percent}%`}
      >
        <span>Óptima</span>
        <span className="font-mono">({percent}%)</span>
      </span>
    )
  }

  return (
    <span
      className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-950/70 text-amber-300 border border-amber-800/60"
      aria-label={`Capacidad holgada estimada: ${percent}%`}
    >
      <span>Baja carga</span>
      <span className="font-mono">({percent}%)</span>
    </span>
  )
}
