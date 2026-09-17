import { env } from '@/config/env'
import { Building2, MapPin, Sparkles } from 'lucide-react'

export function Header() {
  return (
    <header className="h-16 border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-20">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-lg bg-slate-800/70 border border-slate-700/60 text-xs text-slate-300">
          <Building2 className="w-3.5 h-3.5 text-amber-400" />
          <span className="font-semibold text-slate-200">{env.companyName}</span>
          <span className="text-slate-600">|</span>
          <MapPin className="w-3 h-3 text-slate-400" />
          <span className="text-slate-400">{env.storeName}</span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {env.useMocks && (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-950/60 border border-amber-800/50 text-[11px] font-medium text-amber-300">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
            Modo Simulación (Mock Activo)
          </div>
        )}

        <div className="flex items-center gap-2 pl-2 border-l border-slate-800">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-amber-500 to-amber-300 flex items-center justify-center text-slate-950 font-bold text-xs shadow-sm">
            <Sparkles className="w-4 h-4 text-slate-950" />
          </div>
          <div className="hidden sm:block text-left">
            <div className="text-xs font-semibold text-slate-200">Asesor Comercial</div>
            <div className="text-[10px] text-slate-400 font-mono">ID: {env.companyId}</div>
          </div>
        </div>
      </div>
    </header>
  )
}
