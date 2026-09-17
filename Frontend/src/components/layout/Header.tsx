import { Menu } from 'lucide-react'

interface HeaderProps {
  onOpenMobileMenu: () => void
}

export function Header({ onOpenMobileMenu }: HeaderProps) {
  return (
    <header className="h-16 border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md px-4 sm:px-6 flex items-center justify-between sticky top-0 z-20">
      <div className="flex items-center gap-3">
        {/* Mobile menu trigger */}
        <button
          onClick={onOpenMobileMenu}
          className="lg:hidden text-slate-300 hover:text-white p-2 rounded-lg hover:bg-slate-800 focus:outline-none focus:ring-1 focus:ring-amber-500"
          aria-label="Abrir menú de navegación"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-slate-200">
            Plataforma de Priorización
          </span>
          <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700 hidden sm:inline-block">
            Venta de Motocicletas
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700/60 text-xs text-slate-300">
          <span className="w-2 h-2 rounded-full bg-emerald-400" />
          <span className="text-slate-300 font-medium hidden sm:inline">Frontend Base</span>
          <span className="text-[11px] text-slate-400 font-mono">v0.1.0</span>
        </div>
      </div>
    </header>
  )
}
